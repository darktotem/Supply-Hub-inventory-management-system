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