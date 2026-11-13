import os
import re
import sys
from datetime import datetime
from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extensions import db
from models.customer import Customer
from models.inventory import Inventory
from models.invoice import Invoice


@pytest.fixture
def app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def customer(app):
    # Adjust fields to match your Customer model
    c = Customer(name="Test Customer", email="customer@example.com")
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def product(app):
    # Adjust fields to match your Product model
    p = Product(name="Test Product", price=10)
    db.session.add(p)
    db.session.commit()
    return p


def make_invoice(customer, product, **overrides):
    data = {
        "unit_price": Decimal("25.50"),
        "customer_id": customer.id,
        "product_id": product.id,
    }
    data.update(overrides)
    return Invoice(**data)


def test_defaults_are_generated_on_save(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert re.fullmatch(r"\d{16}", invoice.receipt_number)
    assert isinstance(invoice.date_created, datetime)
    assert invoice.quantity == 1


def test_unit_price_is_stored_as_decimal(customer, product):
    invoice = make_invoice(customer, product, unit_price=Decimal("19.99"))
    db.session.add(invoice)
    db.session.commit()
    db.session.refresh(invoice)

    assert invoice.unit_price == Decimal("19.99")


def test_receipt_number_must_be_unique(customer, product):
    db.session.add(make_invoice(customer, product, receipt_number="1234567890123456"))
    db.session.commit()

    db.session.add(make_invoice(customer, product, receipt_number="1234567890123456"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


@pytest.mark.parametrize("missing", ["unit_price", "customer_id", "product_id"])
def test_required_fields_cannot_be_null(customer, product, missing):
    invoice = make_invoice(customer, product, **{missing: None})
    db.session.add(invoice)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_relationships_link_both_ways(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert invoice.customer == customer
    assert invoice.product == product
    assert invoice in customer.invoices
    assert invoice in product.invoices