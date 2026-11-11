from app.extensions import db
from app.models.supplier import Supplier

class SupplyHistory(db.Model):
    __tablename__ = 'supply_history'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date_of_order = db.Column(db.Date, nullable=False)
    date_of_delivery = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')

    # Allows access to the associated supplier
    supplier = db.relationship('Supplier', backref=db.backref('supply_history', lazy=True))
