from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from extensions import db
from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory
from schemas.sales_schema import CustomerSchema, OrderSchema

sales_bp = Blueprint("sales", __name__)

customer_schema = CustomerSchema()
order_schema = OrderSchema()


@sales_bp.get("/api/customers")
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers]), 200


@sales_bp.post("/api/register_customer")
def register_customer():
    try:
        data = customer_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    customer = Customer(
        customer_name=data["customer_name"],
        contact=data["contact"],
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(customer.to_dict()), 201


@sales_bp.delete("/api/delete_customer/<int:id>")
def delete_customer(id):
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    has_orders = CustomerHistory.query.filter_by(customer_id=id).first()
    if has_orders:
        return jsonify({"error": "This customer has orders and cannot be deleted"}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"}), 200



@sales_bp.get("/api/customer_orders")
def get_customer_orders():
    orders = CustomerHistory.query.order_by(CustomerHistory.id.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@sales_bp.get("/api/customer_history")
def get_customer_history():
    history = (
        CustomerHistory.query
        .filter(CustomerHistory.status != "pending")
        .order_by(CustomerHistory.id.desc())
        .all()
    )
    return jsonify([h.to_dict() for h in history]), 200


@sales_bp.post("/api/post_customer_orders")
def post_customer_order():
    try:
        data = order_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    customer = db.session.get(Customer, data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    product = db.session.get(Inventory, data["product_id"])
    if not product:
        return jsonify({"error": "Product not found"}), 404

    quantity = data["quantity"]
    if quantity > product.quantity:
        return jsonify({"error": "Not enough stock. Only " + str(product.quantity) + " left"}), 400

    order = CustomerHistory(
        customer_id=customer.id,
        product_id=product.id,
        quantity=quantity,
        total_price=product.price * quantity,
        status="pending",
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@sales_bp.patch("/api/cancel_customer_order/<int:id>")
def cancel_customer_order(id):
    order = db.session.get(CustomerHistory, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "pending":
        return jsonify({"error": "Only pending orders can be cancelled"}), 400

    order.status = "cancelled"
    db.session.commit()
    return jsonify(order.to_dict()), 200


@sales_bp.patch("/api/fulfil_customer_order/<int:id>")
def fulfil_customer_order(id):
    order = db.session.get(CustomerHistory, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if order.status != "pending":
        return jsonify({"error": "Only pending orders can be fulfilled"}), 400

    if order.quantity > order.product.quantity:
        return jsonify({"error": "Not enough stock to fulfil this order"}), 400

    order.product.quantity = order.product.quantity - order.quantity
    order.status = "fulfilled"
    db.session.commit()
    return jsonify(order.to_dict()), 200