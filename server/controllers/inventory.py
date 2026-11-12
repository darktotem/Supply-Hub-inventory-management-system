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