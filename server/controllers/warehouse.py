from datetime import date

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from extensions import db
from models.inventory import Inventory
from models.supply_history import SupplyHistory
from schemas.warehouse_schema import (
    warehouse_product_schema,
    warehouse_product_update_schema,
)

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

    try:
        validated_data = warehouse_product_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    item = Inventory(**validated_data)

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

    try:
        validated_data = warehouse_product_update_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    for field, value in validated_data.items():
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
