from flask import request, Blueprint, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.inventory import Inventory
from schemas.inventory_schema import inventory_schema, search_schema


inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")


@inventory_bp.post("")
def create_inventory():
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
def get_inventory():
    inventory = Inventory.query.all()
 
    return jsonify(inventory_schema.dump(inventory, many=True)), 200
 
 
@inventory_bp.get("/<int:item_id>")
def get_inventory_item(item_id):
    item = db.session.get(Inventory, item_id)
 
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
 
    return jsonify(inventory_schema.dump(item)), 200
 
 
@inventory_bp.put("/<int:item_id>")
def update_inventory(item_id):
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
def delete_inventory(item_id):
    item = db.session.get(Inventory, item_id)
 
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
 
    db.session.delete(item)
    db.session.commit()
 
    return jsonify({"message": "Inventory item deleted successfully"}), 200
 
 
@inventory_bp.get("/low-stock")
def get_low_stock():
    inventory = Inventory.query.filter(
        Inventory.quantity <= Inventory.threshold
    ).all()
 
    return jsonify(inventory_schema.dump(inventory, many=True)), 200
 
 
@inventory_bp.post("/search")
def search_inventory():
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