from extensions import db 

class SupplyHistory(db.Model):
    __tablename__ = "supply_history"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_of_order = db.Column(db.Date, nullable=False)
    date_of_delivery = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="Pending")

    supplier = db.relationship("Supplier", backref=db.backref("supply_history", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "supplier_id": self.supplier_id,
            "quantity": self.quantity,
            "date_of_order": self.date_of_order.isoformat() if self.date_of_order else None,
            "date_of_delivery": self.date_of_delivery.isoformat() if self.date_of_delivery else None,
            "status": self.status,
            "supplier": self.supplier.to_dict() if self.supplier else None
        }