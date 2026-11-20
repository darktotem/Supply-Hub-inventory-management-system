from flask import request, Blueprint, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from utils.decorators import login_required, roles_required

from models.user import Role
from extensions import db
from models.inventory import Inventory
from schemas.inventory_schema import inventory_schema, search_schema


inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.post("")
@login_required
@roles_required(Role.STORE_WORKER, Role.OPERATIONS_DIRECTOR)
def create_inventory():
    """
    Create an inventory item
    ---
    tags:
      - Inventory
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_name: {type: string}
            category: {type: string}
            quantity: {type: integer}
            threshold: {type: integer}
            price: {type: number}
    responses:
      201:
        description: Item created
      400:
        description: Validation error
    """
    data = request.get_json(silent=True)
 
    if data is None:
        return jsonify({"error": "Request body is required"}), 400
 
    try:
        validated_data = inventory_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
 
    item = Inventory(**validated_data)
 
    db.session.add(item)
    db.session.commit()
 
    return jsonify(inventory_schema.dump(item)), 201


@inventory_bp.get("")
@login_required
def get_inventory():
    """
    List all inventory items
    ---
    tags:
      - Inventory
    responses:
      200:
        description: List of items
    """
    inventory = Inventory.query.all()
 
    return jsonify(inventory_schema.dump(inventory, many=True)), 200
 
 
@inventory_bp.get("/<int:item_id>")
@login_required
def get_inventory_item(item_id):
    """
    Get one inventory item
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: The item
      404:
        description: Not found
    """
    item = db.session.get(Inventory, item_id)
 
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
 
    return jsonify(inventory_schema.dump(item)), 200
 
 
@inventory_bp.put("/<int:item_id>")
@login_required
def update_inventory(item_id):
    """
    Update an inventory item
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_name: {type: string}
            category: {type: string}
            quantity: {type: integer}
            threshold: {type: integer}
            price: {type: number}
    responses:
      200:
        description: Item updated
      404:
        description: Not found
    """
    item = db.session.get(Inventory, item_id)
 
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
 
    data = request.get_json(silent=True)
 
    if data is None:
        return jsonify({"error": "Request body is required"}), 400
 
    try:
        validated_data = inventory_schema.load(data, partial=True)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
 
    for field, value in validated_data.items():
        setattr(item, field, value)
 
    db.session.commit()
 
    return jsonify(inventory_schema.dump(item)), 200
 
 
@inventory_bp.delete("/<int:item_id>")
@login_required
def delete_inventory(item_id):
    """
    Delete an inventory item
    ---
    tags:
      - Inventory
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Item deleted
      404:
        description: Not found
    """
    item = db.session.get(Inventory, item_id)
 
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
 
    db.session.delete(item)
    db.session.commit()
 
    return jsonify({"message": "Inventory item deleted successfully"}), 200
 
 
@inventory_bp.get("/low-stock")
@login_required
def get_low_stock():
    """
    List items at or below their stock threshold
    ---
    tags:
      - Inventory
    responses:
      200:
        description: Low-stock items
    """
    inventory = Inventory.query.filter(
        Inventory.quantity <= Inventory.threshold
    ).all()
 
    return jsonify(inventory_schema.dump(inventory, many=True)), 200
 
 
@inventory_bp.post("/search")
@login_required
def search_inventory():
    """
    Search inventory by product name
    ---
    tags:
      - Inventory
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [product_name]
          properties:
            product_name: {type: string}
    responses:
      200:
        description: Matching items
    """
    data = request.get_json(silent=True)
 
    if data is None:
        return jsonify({"error": "Request body is required"}), 400
 
    try:
        validated_data = search_schema.load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
 
    product_name = validated_data["product_name"]
 
    inventory = Inventory.query.filter(
        Inventory.product_name.ilike(f"%{product_name}%")
    ).all()
 
    return jsonify(inventory_schema.dump(inventory, many=True)), 200