from decimal import Decimal

import pytest
from flask import Flask
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Customer, Invoice, Product


@pytest.fixture
def app():
    """Fresh in-memory database for every test."""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def customer(app):
    c = Customer(name="Amina", email="amina@example.com")
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def product(app):
    p = Product(name="Laptop", price=Decimal("999.99"))
    db.session.add(p)
    db.session.commit()
    return p


def make_invoice(customer, product, **overrides):
    data = {
        "customer_id": customer.id,
        "product_id": product.id,
        "unit_price": product.price,
    }
    data.update(overrides)
    return Invoice(**data)


def test_create_invoice(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert invoice.id is not None
    assert invoice.customer_id == customer.id
    assert invoice.product_id == product.id


def test_default_quantity_is_one(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert invoice.quantity == 1


def test_receipt_number_is_generated(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert len(invoice.receipt_number) == 16
    assert invoice.receipt_number.isdigit()
    assert invoice.receipt_number[0] != "0"


def test_date_created_is_set(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert invoice.date_created is not None


def test_receipt_numbers_differ_between_invoices(customer, product):
    first = make_invoice(customer, product)
    second = make_invoice(customer, product)
    db.session.add_all([first, second])
    db.session.commit()

    assert first.receipt_number != second.receipt_number


def test_duplicate_receipt_number_is_rejected(customer, product):
    db.session.add(make_invoice(customer, product, receipt_number="1234567890123456"))
    db.session.commit()

    db.session.add(make_invoice(customer, product, receipt_number="1234567890123456"))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_unit_price_is_required(customer, product):
    invoice = Invoice(customer_id=customer.id, product_id=product.id)
    db.session.add(invoice)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_customer_is_required(product):
    invoice = Invoice(product_id=product.id, unit_price=product.price)
    db.session.add(invoice)

    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_unit_price_keeps_decimal_value(customer, product):
    invoice = make_invoice(customer, product, unit_price=Decimal("19.99"))
    db.session.add(invoice)
    db.session.commit()
    db.session.refresh(invoice)

    assert invoice.unit_price == Decimal("19.99")


def test_relationships(customer, product):
    invoice = make_invoice(customer, product)
    db.session.add(invoice)
    db.session.commit()

    assert invoice.customer == customer
    assert invoice.product == product
    assert invoice in customer.invoices
    assert invoice in product.invoices