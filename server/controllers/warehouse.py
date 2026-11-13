from datetime import date

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from extensions import db
from models.inventory import Inventory
from models.supply_history import SupplyHistory

warehouse_bp = Blueprint("warehouse", __name__)


def _inventory_to_dict(item):
    return {
        "id": item.id,
        "product_name": item.product_name,
        "category": item.category,
        "quantity": item.quantity,
        "threshold": item.threshold,
        "price": item.price,
    }


@warehouse_bp.route("/warehouse/products", methods=["GET", "POST"])
@warehouse_bp.route("/api/warehouse/products", methods=["GET", "POST"])
@warehouse_bp.route("/products", methods=["GET", "POST"])
@warehouse_bp.route("/api/products", methods=["GET", "POST"])
def warehouse_products():
    if request.method == "GET":
        products = Inventory.query.order_by(Inventory.product_name.asc()).all()
        return jsonify([_inventory_to_dict(item) for item in products]), 200

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body is required"}), 400

    product_name = str(data.get("product_name") or data.get("name") or "").strip()
    category = str(data.get("category") or "").strip()

    if not product_name or not category:
        return jsonify({"error": "product_name and category are required"}), 400

    try:
        quantity = int(data.get("quantity", 0))
        threshold = int(data.get("threshold", 0))
        price = float(data.get("price", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "quantity, threshold and price must be numeric"}), 400

    if quantity < 0 or threshold < 0 or price < 0:
        return jsonify({"error": "quantity, threshold and price cannot be negative"}), 400

    item = Inventory(
        product_name=product_name,
        category=category,
        quantity=quantity,
        threshold=threshold,
        price=price,
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(_inventory_to_dict(item)), 201


@warehouse_bp.route("/warehouse/products/<int:item_id>", methods=["PATCH"])
@warehouse_bp.route("/api/warehouse/products/<int:item_id>", methods=["PATCH"])
@warehouse_bp.route("/products/<int:item_id>", methods=["PATCH"])
@warehouse_bp.route("/api/products/<int:item_id>", methods=["PATCH"])
def update_warehouse_product(item_id):
    item = db.session.get(Inventory, item_id)
    if item is None:
        return jsonify({"error": "Inventory item not found"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body is required"}), 400

    for field in ["product_name", "category"]:
        value = data.get(field)
        if value is not None:
            if field in ["product_name", "category"] and str(value).strip() == "":
                return jsonify({"error": f"{field} cannot be empty"}), 400
            setattr(item, field, value)

    for field in ["quantity", "threshold", "price"]:
        if field in data:
            value = data[field]
            try:
                if field in ["quantity", "threshold"]:
                    value = int(value)
                else:
                    value = float(value)
            except (TypeError, ValueError):
                return jsonify({"error": f"{field} must be numeric"}), 400

            if value < 0:
                return jsonify({"error": f"{field} cannot be negative"}), 400

            setattr(item, field, value)

    db.session.commit()
    return jsonify(_inventory_to_dict(item)), 200


@warehouse_bp.route("/warehouse/deliveries", methods=["GET"])
@warehouse_bp.route("/api/warehouse/deliveries", methods=["GET"])
@warehouse_bp.route("/deliveries", methods=["GET"])
@warehouse_bp.route("/api/deliveries", methods=["GET"])
def warehouse_deliveries():
    orders = SupplyHistory.query.order_by(SupplyHistory.date_of_order.desc()).all()
    return jsonify([order.to_dict() for order in orders]), 200


@warehouse_bp.route("/warehouse/deliveries/<int:order_id>/deliver", methods=["PATCH", "POST"])
@warehouse_bp.route("/api/warehouse/deliveries/<int:order_id>/deliver", methods=["PATCH", "POST"])
@warehouse_bp.route("/deliveries/<int:order_id>/deliver", methods=["PATCH", "POST"])
@warehouse_bp.route("/api/deliveries/<int:order_id>/deliver", methods=["PATCH", "POST"])
def mark_delivery(order_id):
    order = db.session.get(SupplyHistory, order_id)
    if order is None:
        return jsonify({"error": "Supply order not found"}), 404

    if order.status in ["Delivered", "Cancelled"]:
        return jsonify({"error": "This order cannot be marked as delivered"}), 400

    product = db.session.get(Inventory, order.product_id)
    if product is None:
        return jsonify({"error": "Product linked to this order does not exist"}), 404

    product.quantity += order.quantity
    order.status = "Delivered"
    order.date_of_delivery = date.today()
    db.session.commit()

    return jsonify({
        "message": "Delivery received successfully",
        "order": order.to_dict(),
        "inventory": _inventory_to_dict(product),
    }), 200


@warehouse_bp.route("/warehouse/reports", methods=["GET"])
@warehouse_bp.route("/api/warehouse/reports", methods=["GET"])
@warehouse_bp.route("/reports", methods=["GET"])
@warehouse_bp.route("/api/reports", methods=["GET"])
def warehouse_reports():
    inventory = Inventory.query.order_by(Inventory.product_name.asc()).all()
    low_stock_items = [
        _inventory_to_dict(item) for item in inventory if item.quantity <= item.threshold
    ]

    return jsonify({
        "total_products": len(inventory),
        "total_quantity": sum(item.quantity for item in inventory),
        "low_stock_count": len(low_stock_items),
        "low_stock_items": low_stock_items,
        "inventory": [_inventory_to_dict(item) for item in inventory],
    }), 200
