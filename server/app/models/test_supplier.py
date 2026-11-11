import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import app.extensions as extensions

if not hasattr(extensions, "db"):
    extensions.db = SQLAlchemy()

db = extensions.db

from app.models.supplier import Supplier

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


def test_create_supplier(app):
    supplier = Supplier(
        brand_name="ABC Supplies",
        email="abc@example.com",
        telephone="0712345678"
    )

    db.session.add(supplier)
    db.session.commit()

    assert supplier.id is not None
    assert supplier.brand_name == "ABC Supplies"
    assert supplier.email == "abc@example.com"
    assert supplier.telephone == "0712345678"


def test_supplier_email_must_be_unique(app):
    supplier1 = Supplier(
        brand_name="ABC Supplies",
        email="abc@example.com"
    )

    supplier2 = Supplier(
        brand_name="XYZ Supplies",
        email="abc@example.com"
    )

    db.session.add(supplier1)
    db.session.commit()

    db.session.add(supplier2)

    with pytest.raises(Exception):
        db.session.commit()

    db.session.rollback()
