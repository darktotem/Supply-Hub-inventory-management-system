from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from extensions import db
from models.supplier import Supplier
from models.supply_history import SupplyHistory
from models.inventory import Inventory
from schemas.supply_schema import (
    supply_schema,
    supply_order_schema,
    cancel_order_status_schema,
    supply_history_schema
)

supply_bp = Blueprint("supply", __name__)

@supply_bp.route("/supplyhistory", methods=["GET"])
def get_supply_history():
    supply_history = SupplyHistory.query.all()
    result = supply_history_schema.dump(supply_history)

    return jsonify(result), 200

#Register a new supplier
@supply_bp.route("/register_supplier", methods=["POST"])
def register_supplier():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body is required"}), 400

    try:
        validated_data = supply_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400    

    existing_supplier = Supplier.query.filter_by(
        email=validated_data["email"]
    ).first()

    if existing_supplier:
        return jsonify({"error": "Supplier with this email already exists"}), 409

    new_supplier = Supplier(
        name=validated_data["name"],
        contact_person=validated_data["contact_person"],
        phone=validated_data["phone"],
        email=validated_data["email"],
        address=validated_data["address"]
    )

    db.session.add(new_supplier)
    db.session.commit()

    return jsonify(supply_schema.dump(new_supplier)), 201

#Delete a supplier
@supply_bp.route("/delete_suppliers/<int:supplier_id>", methods=["DELETE"])
def delete_supplier(supplier_id):
    supplier = db.session.get(Supplier, supplier_id)

    if supplier is None:
        return jsonify({"error": "Supplier not found"}), 404

    existing_orders = SupplyHistory.query.filter_by(
        supplier_id=supplier_id
    ).first()

    if existing_orders:
        return jsonify({"error": "Cannot delete supplier with existing supply orders"}), 409

    db.session.delete(supplier)
    db.session.commit()

    return jsonify({"message": "Supplier deleted successfully"}), 200

#Create a new supply order
@supply_bp.route("/supply_orders", methods=["POST"])
def create_supply_order():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body is required"}), 400

    try:
        validated_data = supply_order_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    product = db.session.get(Inventory, validated_data["product_id"])

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    supplier = db.session.get(Supplier, validated_data["supplier_id"])

    if supplier is None:
        return jsonify({"error": "Supplier not found"}), 404

    new_supply_order = SupplyHistory(
        product_id=validated_data["product_id"],
        supplier_id=validated_data["supplier_id"],
        quantity=validated_data["quantity"],
        date_of_order=validated_data["date_of_order"]
    )

    db.session.add(new_supply_order)
    db.session.commit()

    return jsonify(new_supply_order.to_dict()), 201

#Cancel an order
@supply_bp.route("/cancel_order/<int:order_id>", methods=["PATCH"])
def cancel_order(order_id):
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Request body is required"}), 400

    try:
        validated_data = cancel_order_status_schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    supply_order = db.session.get(SupplyHistory, order_id)

    if supply_order is None:
        return jsonify({"error": "Supply order not found"}), 404

    if supply_order.status in ["Delivered", "Cancelled"]:
        return jsonify({"error": "This order cannot be cancelled"}), 400

    supply_order.status = validated_data["status"]
    db.session.commit()

    return jsonify({"message": "Supply order cancelled successfully"}), 200
    