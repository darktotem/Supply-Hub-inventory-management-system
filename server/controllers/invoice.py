
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from extensions import db

from models.invoice import Invoice
from models.customer import Customer
from models.product import Product

from schemas.invoice_schema import invoice_schema, invoices_schema


invoice_bp = Blueprint("invoice", __name__, url_prefix="/invoices")


@invoice_bp.route("/", methods=["GET"])
def get_invoices():
    invoices = Invoice.query.all()
    return jsonify(invoices_schema.dump(invoices)), 200


@invoice_bp.route("/", methods=["POST"], strict_slashes=False)
def create_invoice():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        data = invoice_schema.load(payload)

        customer = db.session.get(Customer, data["customer_id"])
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        product = db.session.get(Product, data["product_id"])
        if not product:
            return jsonify({"error": "Product not found"}), 404

        invoice = Invoice(
            unit_price=data["unit_price"],  
            quantity=data["quantity"],
            customer_id=customer.id,
            product_id=product.id,
            status="pending",
        )
        db.session.add(invoice)
        db.session.commit()

        return jsonify({
            "message": "Invoice created successfully",
            "invoice": invoice_schema.dump(invoice),
        }), 201

    except ValidationError as error:
        return jsonify({"errors": error.messages}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "A database constraint was violated"}), 409
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 500