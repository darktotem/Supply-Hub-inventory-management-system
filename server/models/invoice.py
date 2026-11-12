import random
from datetime import datetime, timezone
from extensions import db


def generate_receipt_number():
    return str(random.randint(10**15, 10**16 - 1))
def current_date():
    return datetime.now(timezone.utc)


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key = True)
    receipt_number = db.Column(db.String(16), unique=True, nullable=False,index=True, default=generate_receipt_number)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=current_date)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    customer = db.relationship("Customer", back_populates="invoices")
    product = db.relationship("Product", back_populates="invoices")
