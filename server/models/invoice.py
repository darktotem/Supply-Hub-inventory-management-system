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
    total = db.Column(db.Numeric(12, 2), nullable=False)
    amount_paid = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    status = db.Column(db.String(10), nullable=False, default="pending")

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)    
    sale_id = db.Column(db.Integer, db.ForeignKey("customer_history.id"), nullable=True)

    sale = db.relationship("CustomerHistory", back_populates="invoices")
    customer = db.relationship("Customer", back_populates="invoices")
    product = db.relationship("Inventory", back_populates="invoices")
    payments = db.relationship("Payment", back_populates="invoice")

    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="ck_invoice_quantity_positive"),
        db.CheckConstraint("total >= 0", name="ck_invoice_total_nonneg"),
        db.CheckConstraint("amount_paid >= 0 AND amount_paid <= total", name="ck_invoice_paid_range"),
        db.CheckConstraint("status IN ('pending','partial','paid','void')", name="ck_invoice_status"),
    )

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False, index=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    method = db.Column(db.String(20), nullable=False, default="cash")
    reference = db.Column(db.String(64), unique=True, nullable=True)
    paid_at = db.Column(db.DateTime(timezone=True), nullable=False, default=current_date)

    invoice = db.relationship("Invoice", back_populates="payments")

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="ck_payment_amount_positive"),
        db.CheckConstraint("method IN ('cash','mpesa','bank','card')", name="ck_payment_method"),
    )
