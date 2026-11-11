
import pytest
from datetime import date
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import app.extensions as extensions

if not hasattr(extensions, "db"):
    extensions.db = SQLAlchemy()

db = extensions.db

from app.models.supplier import Supplier
from app.models.supply_history import SupplyHistory


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)


@pytest.fixture
def app():
    test_app = Flask(__name__)
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(test_app)

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

def test_create_supply_history(app):
    product = Product(product_name="Laptop")
    supplier = Supplier(
        brand_name="ABC Supplies",
        email="abc@example.com"
    )

    db.session.add_all([product, supplier])
    db.session.commit()

    supply = SupplyHistory(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=20,
        date_of_order=date(2026, 11, 11)
    )

    db.session.add(supply)
    db.session.commit()

    assert supply.id is not None
    assert supply.product_id == product.id
    assert supply.supplier_id == supplier.id
    assert supply.quantity == 20
    assert supply.supplier.brand_name == "ABC Supplies"


def test_default_supply_status(app):
    supply = SupplyHistory(
        product_id=1,
        supplier_id=1,
        quantity=10,
        date_of_order=date(2026, 11, 11)
    )

    db.session.add(supply)
    db.session.commit()

    assert supply.status == "Pending"


def test_delivery_date_can_be_empty(app):
    supply = SupplyHistory(
        product_id=1,
        supplier_id=1,
        quantity=5,
        date_of_order=date(2026, 11, 11)
    )

    db.session.add(supply)
    db.session.commit()

    assert supply.date_of_delivery is None

