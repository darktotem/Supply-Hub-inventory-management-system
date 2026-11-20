from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import update
from extensions import db
from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory
from models.user import Role
from schemas.sales_schema import CustomerSchema, OrderSchema
from utils.stock import take_stock

sales_bp = Blueprint("sales", __name__)

customer_schema = CustomerSchema()
order_schema = OrderSchema()

# TODO (Phase 3): the sales officer and the operations director can use every route.
# The finance officer and the auditor only need GET /api/customer_history.


# ---------- Customers ----------

@sales_bp.get("/api/customers")
@login_required
def get_customers():
    """
    List customers
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    responses:
      200:
        description: List of customers
    """
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers]), 200


@sales_bp.post("/api/register_customer")
@login_required
@roles_required(Role.SALES, Role.OPERATIONS_DIRECTOR)
def register_customer():
    """
    Register a new customer
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [customer_name, contact]
          properties:
            customer_name: {type: string}
            contact: {type: string}
    responses:
      201:
        description: Customer created
      400:
        description: Validation error
    """
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
@login_required
@roles_required(Role.SALES, Role.OPERATIONS_DIRECTOR)
def delete_customer(id):
    """
    Delete a customer (Sales, Operations Director)
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted
      404:
        description: Not found
    """
    customer = db.session.get(Customer, id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    has_orders = CustomerHistory.query.filter_by(customer_id=id).first()
    if has_orders:
        return jsonify({"error": "This customer has orders and cannot be deleted"}), 400

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted"}), 200


# ---------- Customer orders ----------

@sales_bp.get("/api/customer_orders")
@login_required
def get_customer_orders():
    """
    List customer orders
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    responses:
      200:
        description: List of orders
    """
    orders = CustomerHistory.query.order_by(CustomerHistory.id.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@sales_bp.get("/api/customer_history")
@login_required
def get_customer_history():
    """
    List customer order history
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    responses:
      200:
        description: Order history
    """
    history = (
        CustomerHistory.query
        .filter(CustomerHistory.status != "pending")
        .order_by(CustomerHistory.id.desc())
        .all()
    )
    return jsonify([h.to_dict() for h in history]), 200


@sales_bp.post("/api/post_customer_orders")
@login_required
@roles_required(Role.SALES, Role.OPERATIONS_DIRECTOR)
def post_customer_order():
    """
    Create a customer order (Sales, Operations Director)
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [customer_id, product_id, quantity]
          properties:
            customer_id: {type: integer}
            product_id: {type: integer}
            quantity: {type: integer}
    responses:
      201:
        description: Order created
      400:
        description: Validation error or insufficient stock
    """
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
@login_required
@roles_required(Role.SALES, Role.OPERATIONS_DIRECTOR)
def cancel_customer_order(id):
    """
    Cancel a customer order (Sales, Operations Director)
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order cancelled
      404:
        description: Not found
    """
    order = db.session.get(CustomerHistory, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Change the status only if the order is still pending (one step, in the database)
    claimed = db.session.execute(
        update(CustomerHistory)
        .where(CustomerHistory.id == id, CustomerHistory.status == "pending")
        .values(status="cancelled")
        .execution_options(synchronize_session=False)
    )
    if claimed.rowcount == 0:
        db.session.rollback()
        return jsonify({"error": "Only pending orders can be cancelled"}), 400

    db.session.commit()
    order = db.session.get(CustomerHistory, id)
    return jsonify(order.to_dict()), 200


@sales_bp.patch("/api/fulfil_customer_order/<int:id>")
@login_required
@roles_required(Role.SALES, Role.OPERATIONS_DIRECTOR)
def fulfil_customer_order(id):
    """
    Fulfil a customer order (Sales, Operations Director)
    ---
    tags:
      - Sales
    security:
      - Bearer: []
    parameters:
      - name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Order fulfilled
      404:
        description: Not found
    """
    order = db.session.get(CustomerHistory, id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Step 1: claim the order. Only one request can move it from pending to fulfilled.
    claimed = db.session.execute(
        update(CustomerHistory)
        .where(CustomerHistory.id == id, CustomerHistory.status == "pending")
        .values(status="fulfilled")
        .execution_options(synchronize_session=False)
    )
    if claimed.rowcount == 0:
        db.session.rollback()
        return jsonify({"error": "Only pending orders can be fulfilled"}), 400

    # Step 2: take the stock, but only if enough is in the database right now.
    if not take_stock(order.product_id, order.quantity):
        db.session.rollback()  # this also undoes the claim in step 1
        return jsonify({"error": "Not enough stock to fulfil this order"}), 400

    db.session.commit()
    order = db.session.get(CustomerHistory, id)
    return jsonify(order.to_dict()), 200