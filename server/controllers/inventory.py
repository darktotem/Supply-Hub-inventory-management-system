from flask import request
from marshmallow import ValidationError
from app import app
from extensions import db
from models.inventory import Inventory
from schemas.inventory_schema import InventorySchema


inventory_schema = InventorySchema()


@app.post("/api/inventory")
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

@app.get("/api/inventory")
def get_inventory():
    inventory = Inventory.query.all()

    return inventory_schema.dump(inventory, many=True), 200


@app.get("/api/inventory/<int:item_id>")
def get_inventory_item(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return {"error": "Inventory item not found"}, 404

    return inventory_schema.dump(item), 200

