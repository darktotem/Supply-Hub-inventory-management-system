
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from extensions import db

from models.invoice import Invoice, Payment
from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory

from schemas.invoice_schema import invoice_schema, invoices_schema, payment_schema, payments_schema
from utils.finance import money, refresh_status, log_audit

invoice_bp = Blueprint("invoice", __name__, url_prefix="/invoices")


@invoice_bp.route("/", methods=["GET"])
def get_invoices():
    """
    List invoices
    ---
    tags:
      - Invoices
    responses:
      200:
        description: List of invoices
    """
    invoices = Invoice.query.all()
    return jsonify(invoices_schema.dump(invoices)), 200


@invoice_bp.route("/", methods=["POST"], strict_slashes=False)
def create_invoice():
    """
    Create an invoice for a sale
    ---
    tags:
      - Invoices
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [customer_id, product_id, sale_id, unit_price, quantity]
          properties:
            customer_id: {type: integer}
            product_id: {type: integer}
            sale_id: {type: integer}
            unit_price: {type: string, example: "100.00"}
            quantity: {type: integer}
            total: {type: string, example: "100.00"}
    responses:
      201:
        description: Invoice created
      400:
        description: Validation error
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        data = invoice_schema.load(payload)

        customer = db.session.get(Customer, data["customer_id"])
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        product = db.session.get(Inventory, data["product_id"])
        if not product:
            return jsonify({"error": "Product not found"}), 404
        sale = db.session.get(CustomerHistory, data["sale_id"], with_for_update=True)
        if not sale:
            return jsonify({"error": "Sale not found"}), 404

  
        if sale.customer_id != customer.id:
            return jsonify({"error": "Invoice customer does not match the sale"}), 422
        if sale.product_id != product.id:
            return jsonify({"error": "Invoice product does not match the sale"}), 422


        total = money(data["unit_price"]) * data["quantity"]
        if "total" in data and money(data["total"]) != total:
            return jsonify({"error": "Total does not match quantity x unit_price", "expected": str(total)}), 422


        inv_qty, inv_total = db.session.query(
            func.coalesce(func.sum(Invoice.quantity), 0),
            func.coalesce(func.sum(Invoice.total), 0),
        ).filter(Invoice.sale_id == sale.id, Invoice.status != "void").one()

        if inv_qty + data["quantity"] > sale.quantity:
            return jsonify({"error": "Invoiced quantity would exceed the sale quantity"}), 422
        if money(inv_total) + total > money(sale.total_price):
            return jsonify({"error": "Invoiced amount would exceed the sale total"}), 422

        invoice = Invoice(
            unit_price=money(data["unit_price"]),
            quantity=data["quantity"],
            total=total,
            customer_id=customer.id,
            product_id=product.id,
            sale_id=sale.id,
        )
        db.session.add(invoice)
        db.session.flush()  
        log_audit("invoice", invoice.id, "create", None, {"total": str(total), "sale_id": sale.id})
        db.session.commit()

        return jsonify({"message": "Invoice created successfully", "invoice": invoice_schema.dump(invoice)}), 201

    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A database constraint was violated"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500


@invoice_bp.route("/<int:invoice_id>/payments", methods=["GET"])
def get_payments(invoice_id):
    """
    List payments for an invoice
    ---
    tags:
      - Invoices
    parameters:
      - name: invoice_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: List of payments
      404:
        description: Invoice not found
    """
    invoice = db.session.get(Invoice, invoice_id)
    if not invoice:
        return jsonify({"error": "Invoice not found"}), 404
    return jsonify(payments_schema.dump(invoice.payments)), 200


@invoice_bp.route("/<int:invoice_id>/payments", methods=["POST"])
def add_payment(invoice_id):
    """
    Add a payment to an invoice
    ---
    tags:
      - Invoices
    parameters:
      - name: invoice_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [amount]
          properties:
            amount: {type: string, example: "50.00"}
            method: {type: string, enum: [cash, mpesa, bank, card]}
            reference: {type: string}
    responses:
      201:
        description: Payment recorded
      400:
        description: Validation error
      404:
        description: Invoice not found
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        data = payment_schema.load(payload)

        invoice = db.session.get(Invoice, invoice_id, with_for_update=True)
        if not invoice:
            return jsonify({"error": "Invoice not found"}), 404
        if invoice.status in ("paid", "void"):
            return jsonify({"error": f"Invoice is already {invoice.status}"}), 409

        amount = money(data["amount"])
        balance = invoice.total - invoice.amount_paid
        if amount > balance:
            return jsonify({"error": "Payment exceeds the balance due", "balance_due": str(balance)}), 422

        old = {"amount_paid": str(invoice.amount_paid), "status": invoice.status}

        payment = Payment(invoice_id=invoice.id, amount=amount, method=data["method"], reference=data.get("reference"))
        db.session.add(payment)
        invoice.amount_paid += amount
        refresh_status(invoice)
        db.session.flush()

        log_audit(
            "invoice", 
            invoice.id, 
            "payment", old,
            {"amount_paid": str(invoice.amount_paid), 
            "status": invoice.status,
            "payment_id": payment.id, 
            "payment_amount": str(amount)})
        db.session.commit()

        return jsonify({
            "message": "Payment recorded",
            "payment": payment_schema.dump(payment),
            "invoice": invoice_schema.dump(invoice)
        }), 201

    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Duplicate payment reference or constraint violation"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500