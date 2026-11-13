from extensions import db


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String, nullable=False)
    contact = db.Column(db.String, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "contact": self.contact,
        }