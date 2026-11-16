from datetime import datetime

from extensions import db
from models.inventory import Inventory


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(50), nullable=False, default="inventory")
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_products = db.Column(db.Integer, nullable=False)
    total_quantity = db.Column(db.Integer, nullable=False)
    low_stock_count = db.Column(db.Integer, nullable=False)
    low_stock_items = db.Column(db.JSON, nullable=False)
    inventory = db.Column(db.JSON, nullable=False)

    @classmethod
    def create_inventory_report(cls):
        items = Inventory.query.order_by(Inventory.product_name.asc()).all()
        inventory = [
            {
                "id": item.id,
                "product_name": item.product_name,
                "category": item.category,
                "quantity": item.quantity,
                "threshold": item.threshold,
                "price": item.price,
            }
            for item in items
        ]
        low_stock_items = [
            item for item in inventory if item["quantity"] <= item["threshold"]
        ]

        return cls(
            generated_at=datetime.utcnow(),
            total_products=len(inventory),
            total_quantity=sum(item["quantity"] for item in inventory),
            low_stock_count=len(low_stock_items),
            low_stock_items=low_stock_items,
            inventory=inventory,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "report_type": self.report_type,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "total_products": self.total_products,
            "total_quantity": self.total_quantity,
            "low_stock_count": self.low_stock_count,
            "low_stock_items": self.low_stock_items,
            "inventory": self.inventory,
        }