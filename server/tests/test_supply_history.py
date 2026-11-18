
import pytest
from extensions import db
from models.user import Role
from app import app as flask_app

from models.customer import Customer
from models.inventory import Inventory
from models.inventory import Inventory
from models.supplier import Supplier
from models.supply_history import SupplyHistory


# |-------------------------MISSING CUSTOMER AND PRODUCT FIXTURES----------------|
@pytest.fixture
def customer(database):
    customer = Customer(
        customer_name="Amina Wanjiru",
        contact="0723456789"
    )

    database.session.add(customer)
    database.session.commit()

    return customer


@pytest.fixture
def product(database):
    product = Inventory(
        product_name="Laptop",
        category="Electronics",
        quantity=10,
        threshold=5,
        price=350
    )

    database.session.add(product)
    database.session.commit()

    return product
# --------------------------------------------------------------------------------

def make_order(client, customer, product, headers, quantity=2):
    response = client.post(
        "/api/post_customer_orders",
        json={
            "customer_id": customer.id,
            "product_id": product.id,
            "quantity": quantity,
        },
        headers=headers,
    )
    return response.get_json()



def sales_headers(user_factory, username="sales", role=Role.SALES):
    user_data = user_factory(role=role, username=username)
    return user_data["headers"]

# ---------- Customers ----------

def test_get_customers_empty(client, user_factory):
    headers = sales_headers(user_factory)

    response = client.get("/api/customers", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_customers_returns_customer(client, customer, user_factory):
    headers = sales_headers(user_factory)
    response = client.get("/api/customers", headers=headers)

    assert response.status_code == 200
    assert response.get_json()[0]["customer_name"] == "Amina Wanjiru"


def test_register_customer(client, make_user, auth_header):
    headers = sales_headers(make_user, auth_header)
def test_register_customer(client, sales_user):
    headers = sales_user["headers"]
    response = client.post(
        "/api/register_customer",
        json={"customer_name": "Brian Otieno", "contact": "0723456789"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.get_json()["customer_name"] == "Brian Otieno"


def test_register_customer_invalid_data(client, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/register_customer",
        json={"customer_name": "", "contact": "abc"},
        headers=headers,
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_delete_customer(client, customer, user_factory):
    headers = sales_headers(user_factory)
    response = client.delete(f"/api/delete_customer/{customer.id}", headers=headers)

    assert response.status_code == 200
    assert client.get("/api/customers", headers=headers).get_json() == []


def test_delete_customer_not_found(client, user_factory):
    headers = sales_headers(user_factory)
    response = client.delete("/api/delete_customer/999", headers=headers)

    assert response.status_code == 404


def test_delete_customer_with_orders_is_blocked(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    make_order(client, customer, product, headers)

    response = client.delete(f"/api/delete_customer/{customer.id}", headers=headers)

    assert response.status_code == 400


# ---------- Creating orders ----------

def test_create_order(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/post_customer_orders",
        json={"customer_id": customer.id, "product_id": product.id, "quantity": 2},
        headers=headers,
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["status"] == "pending"
    assert data["total_price"] == 700
    assert product.quantity == 10


def test_create_order_not_enough_stock(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/post_customer_orders",
        json={"customer_id": customer.id, "product_id": product.id, "quantity": 11},
        headers=headers,
    )

    assert response.status_code == 400


def test_create_order_unknown_customer(client, product, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/post_customer_orders",
        json={"customer_id": 999, "product_id": product.id, "quantity": 1},
        headers=headers,
    )

    assert response.status_code == 404


def test_create_order_unknown_product(client, customer, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/post_customer_orders",
        json={"customer_id": customer.id, "product_id": 999, "quantity": 1},
        headers=headers,
    )

    assert response.status_code == 404


def test_create_order_invalid_quantity(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    response = client.post(
        "/api/post_customer_orders",
        json={"customer_id": customer.id, "product_id": product.id, "quantity": 0},
        headers=headers,
    )

    assert response.status_code == 400


def test_orders_are_listed_newest_first(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    first = make_order(client, customer, product, headers)
    second = make_order(client, customer, product, headers)

    response = client.get("/api/customer_orders", headers=headers)
    orders = response.get_json()

    assert response.status_code == 200
    assert orders[0]["id"] == second["id"]
    assert orders[1]["id"] == first["id"]


# ---------- Cancelling orders ----------

def test_cancel_order(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers)

    response = client.patch(f"/api/cancel_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 200
    assert response.get_json()["status"] == "cancelled"


def test_cancel_order_twice_is_blocked(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers)
    client.patch(f"/api/cancel_customer_order/{order['id']}", headers=headers)

    response = client.patch(f"/api/cancel_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 400


def test_cancel_order_not_found(client, user_factory):
    headers = sales_headers(user_factory)
    response = client.patch("/api/cancel_customer_order/999", headers=headers)

    assert response.status_code == 404


# ---------- Fulfilling orders ----------

def test_fulfil_order_reduces_stock(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers, quantity=2)

    response = client.patch(f"/api/fulfil_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 200
    assert response.get_json()["status"] == "fulfilled"
    assert product.quantity == 8


def test_fulfil_order_twice_is_blocked(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers, quantity=2)
    client.patch(f"/api/fulfil_customer_order/{order['id']}", headers=headers)

    response = client.patch(f"/api/fulfil_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 400
    assert product.quantity == 8


def test_fulfil_cancelled_order_is_blocked(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers)
    client.patch(f"/api/cancel_customer_order/{order['id']}", headers=headers)

    response = client.patch(f"/api/fulfil_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 400


def test_fulfil_order_when_stock_dropped(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    order = make_order(client, customer, product, headers, quantity=8)

    product.quantity = 3
    db.session.commit()

    response = client.patch(f"/api/fulfil_customer_order/{order['id']}", headers=headers)

    assert response.status_code == 400
    assert product.quantity == 3


def test_fulfil_order_not_found(client, user_factory):
    headers = sales_headers(user_factory)
    response = client.patch("/api/fulfil_customer_order/999", headers=headers)

    assert response.status_code == 404


# ---------- Customer history ----------

def test_customer_history_empty(client, user_factory):
    headers = sales_headers(user_factory)
    response = client.get("/api/customer_history", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_customer_history_only_shows_finished_orders(client, customer, product, user_factory):
    headers = sales_headers(user_factory)
    pending = make_order(client, customer, product, headers)
    fulfilled = make_order(client, customer, product, headers)
    cancelled = make_order(client, customer, product, headers)
    client.patch(f"/api/fulfil_customer_order/{fulfilled['id']}", headers=headers)
    client.patch(f"/api/cancel_customer_order/{cancelled['id']}", headers=headers)

    response = client.get("/api/customer_history", headers=headers)
    ids = [h["id"] for h in response.get_json()]

    assert response.status_code == 200
    assert pending["id"] not in ids
    assert ids == [cancelled["id"], fulfilled["id"]]

