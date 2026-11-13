from datetime import datetime
from extensions import db


class CustomerHistory(db.Model):
    __tablename__ = "customer_history"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("inventory.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_of_sale = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String, default="pending")

    customer = db.relationship("Customer")
    product = db.relationship("Inventory")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.customer_name,
            "product_id": self.product_id,
            "product_name": self.product.product_name,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "date_of_sale": self.date_of_sale.isoformat(),
            "status": self.status,
        }