import pytest
from flask import Flask
from extensions import db
from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory
from controllers.sales import sales_bp


@pytest.fixture
def app():
    # A small test app with a temporary in-memory database
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    db.init_app(app)
    app.register_blueprint(sales_bp)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def customer(app):
    c = Customer(customer_name="Amina Wanjiru", contact="0712345678")
    db.session.add(c)
    db.session.commit()
    return c


@pytest.fixture
def product(app):
    p = Inventory(
        product_name="Rice 2kg",
        category="Food",
        quantity=10,
        threshold=2,
        price=350,
    )
    db.session.add(p)
    db.session.commit()
    return p