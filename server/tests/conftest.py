
import pytest
from pathlib import Path

from app import app as flask_app
from extensions import db

from models.supplier import Supplier
from models.supply_history import SupplyHistory
from models.user import Role


from models import (
    Customer,
    Inventory,
    CustomerHistory,
    Invoice,
)
from models.user import User, Role
from utils.tokens import create_token

flask_app.config.update(
    TESTING=True,
    SQLALCHEMY_DATABASE_URI=f"sqlite:///inventory.db",
    SECRET_KEY="test-secret-key-with-at-least-32-bytes",
    JWT_SECRET_KEY="test-jwt-secret-with-at-least-32-bytes"
)

# --------------------------------------------------
# APPLICATION FIXTURES
# --------------------------------------------------

@pytest.fixture(scope="session")
def app(tmp_path_factory):
    test_db = tmp_path_factory.mktemp("test_db") / "test_inventory.db"

    flask_app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{test_db}",
        SECRET_KEY="test-secret-key",
        JWT_SECRET_KEY="test-jwt-secret",
    )

    yield flask_app


@pytest.fixture()
def procurement_user(user_factory):
    return user_factory(
        role=Role.PROCUREMENT,
        username="procurement_user"
    )


@pytest.fixture()
def database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        yield db

        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app, database):
    return app.test_client()


# --------------------------------------------------
# USER / AUTHENTICATION FIXTURES
# --------------------------------------------------

@pytest.fixture()
def user_factory(database):
    """Create users with valid password hashes and JWT tokens."""

    def create_user(role=Role.SALES, username=None, is_active=True):
        username = username or f"user_{role}"

        user = User(
            name="Test User",
            username=username,
            email=f"{username}@example.com",
            role=role,
            is_active=is_active,
        )

        user.set_password("TestPassword123!")

        database.session.add(user)
        database.session.commit()

        token = create_token(user)

        return {
            "user": user,
            "token": token,
            "headers": {
                "Authorization": f"Bearer {token}"
            },
        }

    return create_user


@pytest.fixture()
def sales_user(user_factory):
    return user_factory(
        role=Role.SALES,
        username="sales_user"
    )


@pytest.fixture()
def operations_user(user_factory):
    return user_factory(
        role=Role.OPERATIONS_DIRECTOR,
        username="operations_user"
    )


@pytest.fixture()
def it_admin_user(user_factory):
    return user_factory(
        role=Role.IT_ADMIN,
        username="it_admin"
    )


@pytest.fixture()
def inactive_sales_user(user_factory):
    return user_factory(
        role=Role.SALES,
        username="inactive_sales",
        is_active=False
    )


# --------------------------------------------------
# SALES DATA FIXTURES
# --------------------------------------------------

@pytest.fixture()
def sales_data(database):
    customer = Customer(
        customer_name="John Doe",
        contact="0712345678",
    )

    product = Inventory(
        product_name="Laptop",
        category="Electronics",
        quantity=50,
        threshold=5,
        price=100.00,
    )

    database.session.add_all([customer, product])
    database.session.flush()

    sale = CustomerHistory(
        customer_id=customer.id,
        product_id=product.id,
        quantity=10,
        total_price=1000.00,
        status="pending",
    )

    database.session.add(sale)
    database.session.commit()

    return {
        "customer": customer,
        "product": product,
        "sale": sale,
    }


@pytest.fixture()
def invoice(database, sales_data):
    sale = sales_data["sale"]

    invoice = Invoice(
        customer_id=sales_data["customer"].id,
        product_id=sales_data["product"].id,
        sale_id=sale.id,
        quantity=2,
        unit_price=100.00,
        total=200.00,
    )

    database.session.add(invoice)
    database.session.commit()

    return invoice
