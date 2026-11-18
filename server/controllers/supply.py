from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from extensions import db
from models.inventory import Inventory
from models.supplier import Supplier
from models.supply_history import SupplyHistory
from models.user import Role
from schemas.supply_schema import (
    supply_schema,
    supply_order_schema,
    cancel_order_status_schema,
    supply_history_schema
)
from utils.decorators import login_required, roles_required

supply_bp = Blueprint("supply", __name__)

#Get supply history
@supply_bp.route("/supplyhistory", methods=["GET"])
@login_required
def get_supply_history():
    """
    List supply history
    ---
    tags:
      - Supply
    security:
      - Bearer: []
    responses:
      200:
        description: Supply orders
    """
    supply_history = SupplyHistory.query.all()
    result = supply_history_schema.dump(supply_history)

    return jsonify(result), 200

#Get all registered suppliers
@supply_bp.route("/suppliers", methods=["GET"])
@login_required
def get_suppliers():
    suppliers = Supplier.query.all()
    result = supply_schema.dump(suppliers, many=True)

    return jsonify(result), 200

#Register a new supplier
@supply_bp.route("/register_supplier", methods=["POST"])
@login_required
@roles_required(Role.PROCUREMENT, Role.OPERATIONS_DIRECTOR)
def register_supplier():
    """
    Register a supplier (Procurement, Operations Director)
    ---
    tags:
      - Supply
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: {type: string}
            contact_person: {type: string}
            phone: {type: string}
            email: {type: string}
            address: {type: string}
    responses:
      201:
        description: Supplier registered
      400:
        description: Validation error
    """
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
@login_required
@roles_required(Role.PROCUREMENT, Role.OPERATIONS_DIRECTOR)
def delete_supplier(supplier_id):
    """
    Delete a supplier (Procurement, Operations Director)
    ---
    tags:
      - Supply
    security:
      - Bearer: []
    parameters:
      - name: supplier_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Supplier deleted
      404:
        description: Not found
    """
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
@login_required
@roles_required(Role.PROCUREMENT, Role.OPERATIONS_DIRECTOR)
def create_supply_order():
    """
    Create a supply order (Procurement, Operations Director)
    ---
    tags:
      - Supply
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_id: {type: integer}
            supplier_id: {type: integer}
            quantity: {type: integer}
            date_of_order: {type: string, format: date}
    responses:
      201:
        description: Order created
      404:
        description: Product or supplier not found
    """
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
@login_required
@roles_required(Role.PROCUREMENT, Role.OPERATIONS_DIRECTOR)
def cancel_order(order_id):
    """
    Cancel a pending supply order (Procurement, Operations Director)
    ---
    tags:
      - Supply
    security:
      - Bearer: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            status: {type: string, example: Cancelled}
    responses:
      200:
        description: Order cancelled
      400:
        description: Order cannot be cancelled
      404:
        description: Not found
    """
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

    if supply_order.status != "Pending":
        return jsonify({"error": "This order cannot be cancelled"}), 400

    supply_order.status = "Cancelled"
    db.session.commit()

    return jsonify({"message": "Supply order cancelled successfully"}), 200
    