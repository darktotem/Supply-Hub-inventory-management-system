from flask import request, jsonify
from app import app
from extensions import db
from models.inventory import Inventory


@app.route("/api/inventory", methods=["POST"])
def add_inventory():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = ["product_name", "category", "quantity", "threshold", "price"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    if data["quantity"] < 0 or data["threshold"] < 0 or data["price"] < 0:
        return jsonify({"error": "Values cannot be negative"}), 400

    item = Inventory(
        product_name=data["product_name"],
        category=data["category"],
        quantity=data["quantity"],
        threshold=data["threshold"],
        price=data["price"]
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Inventory item added successfully",
        "id": item.id,
        "product_name": item.product_name,
        "category": item.category,
        "quantity": item.quantity,
        "threshold": item.threshold,
        "price": item.price
    }), 201

    @app.route("/api/inventory", methods=["GET"])
def get_inventory():
    inventory = Inventory.query.all()

    return jsonify([
        {
            "id": item.id,
            "product_name": item.product_name,
            "category": item.category,
            "quantity": item.quantity,
            "threshold": item.threshold,
            "price": item.price
        }
        for item in inventory
    ]), 200


    @app.route("/api/inventory/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    return jsonify({
        "id": item.id,
        "product_name": item.product_name,
        "category": item.category,
        "quantity": item.quantity,
        "threshold": item.threshold,
        "price": item.price
    }), 200


    @app.route("/api/inventory/<int:item_id>", methods=["PUT"])
def update_inventory(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    for field in ["product_name", "category", "quantity", "threshold", "price"]:
        if field in data:
            if field in ["quantity", "threshold", "price"] and data[field] < 0:
                return jsonify({"error": "Values cannot be negative"}), 400

            setattr(item, field, data[field])

    db.session.commit()

    return jsonify({
        "message": "Inventory item updated successfully",
        "id": item.id,
        "product_name": item.product_name,
        "category": item.category,
        "quantity": item.quantity,
        "threshold": item.threshold,
        "price": item.price
    }), 200


    @app.route("/api/inventory/<int:item_id>", methods=["DELETE"])
def delete_inventory(item_id):
    item = db.session.get(Inventory, item_id)

    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Inventory item deleted successfully"}), 200

    @app.route("/api/inventory/low-stock", methods=["GET"])
def get_low_stock():
    inventory = Inventory.query.filter(
        Inventory.quantity <= Inventory.threshold
    ).all()

    return jsonify([
        {
            "id": item.id,
            "product_name": item.product_name,
            "category": item.category,
            "quantity": item.quantity,
            "threshold": item.threshold,
            "price": item.price
        }
        for item in inventory
    ]), 200


    """
INVENTORY ROUTES

1. CREATE INVENTORY ITEM
   Method: POST
   Endpoint: /api/inventory

2. VIEW ALL INVENTORY ITEMS
   Method: GET
   Endpoint: /api/inventory

3. VIEW ONE INVENTORY ITEM
   Method: GET
   Endpoint: /api/inventory/<id>

4. UPDATE INVENTORY ITEM
   Method: PUT
   Endpoint: /api/inventory/<id>

5. DELETE INVENTORY ITEM
   Method: DELETE
   Endpoint: /api/inventory/<id>

6. RETRIEVE LOW-STOCK ITEMS
   Method: GET
   Endpoint: /api/inventory/low-stock
"""