
from flask import Blueprint, request
from marshmallow import ValidationError

from extensions import db
from models.inventory import Inventory
from schemas.inventory_schema import inventory_schema, search_schema


inventory_bp = Blueprint("inventory", __name__, url_prefix="/api")


@inventory_bp.post("/inventory")
def create_inventory():
    data = request.get_json(silent=True)

    if data is None:
        return {"error": "Request body is required"}, 400

    try:
        validated_data = inventory_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    item = Inventory(**validated_data)

    db.session.add(item)
    db.session.commit()

    return inventory_schema.dump(item), 201


@inventory_bp.get("/inventory")
def get_inventory():
    inventory = Inventory.query.all()

    return inventory_schema.dump(inventory, many=True), 200


@inventory_bp.get("/inventory/<int:item_id>")
def get_inventory_item(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return {"error": "Inventory item not found"}, 404

    return inventory_schema.dump(item), 200


@inventory_bp.put("/inventory/<int:item_id>")
def update_inventory(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return {"error": "Inventory item not found"}, 404

    data = request.get_json(silent=True)

    if data is None:
        return {"error": "Request body is required"}, 400

    try:
        validated_data = inventory_schema.load(data, partial=True)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    for field, value in validated_data.items():
        setattr(item, field, value)

    db.session.commit()

    return inventory_schema.dump(item), 200


@inventory_bp.delete("/inventory/<int:item_id>")
def delete_inventory(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return {"error": "Inventory item not found"}, 404

    db.session.delete(item)
    db.session.commit()

    return {"message": "Inventory item deleted successfully"}, 200


@inventory_bp.get("/inventory/low-stock")
def get_low_stock():
    inventory = Inventory.query.filter(
        Inventory.quantity <= Inventory.threshold
    ).all()

    return inventory_schema.dump(inventory, many=True), 200


@inventory_bp.post("/search")
def search_inventory():
    data = request.get_json(silent=True)

    if data is None:
        return {"error": "Request body is required"}, 400

    try:
        validated_data = search_schema.load(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    product_name = validated_data["product_name"]

    inventory = Inventory.query.filter(
        Inventory.product_name.ilike(f"%{product_name}%")
    ).all()

    return inventory_schema.dump(inventory, many=True), 200
