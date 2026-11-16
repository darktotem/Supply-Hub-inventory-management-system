from datetime import date

import pytest

from extensions import db
from models.supplier import Supplier
from models.supply_history import SupplyHistory
from controllers.warehouse import warehouse_bp
from controllers.supply import supply_bp


@pytest.fixture
def stock_client(app):
    # The shared test app only has the sales routes. Add the warehouse and supply routes.
    app.register_blueprint(warehouse_bp)
    app.register_blueprint(supply_bp)
    return app.test_client()


@pytest.fixture
def supplier(app):
    s = Supplier(
        name="Fresh Foods Ltd",
        contact_person="Jane Doe",
        phone="0700000000",
        email="jane@example.com",
        address="Nairobi",
    )
    db.session.add(s)
    db.session.commit()
    return s


def make_supply_order(product, supplier, quantity=5):
    order = SupplyHistory(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=quantity,
        date_of_order=date.today(),
    )
    db.session.add(order)
    db.session.commit()
    return order


def deliver(client, order):
    return client.patch("/api/warehouse/deliveries/" + str(order.id) + "/deliver")


def cancel(client, order):
    return client.patch(
        "/cancel_order/" + str(order.id),
        json={"status": "Cancelled"},
    )


def test_delivery_adds_stock(stock_client, product, supplier):
    order = make_supply_order(product, supplier, quantity=5)

    response = deliver(stock_client, order)

    assert response.status_code == 200
    assert product.quantity == 15
    assert order.status == "Delivered"
    assert order.date_of_delivery == date.today()


def test_delivering_twice_adds_stock_only_once(stock_client, product, supplier):
    order = make_supply_order(product, supplier, quantity=5)
    deliver(stock_client, order)

    response = deliver(stock_client, order)

    assert response.status_code == 400
    assert product.quantity == 15


def test_two_deliveries_of_the_same_product_both_count(stock_client, product, supplier):
    first = make_supply_order(product, supplier, quantity=5)
    second = make_supply_order(product, supplier, quantity=3)

    deliver(stock_client, first)
    deliver(stock_client, second)

    assert product.quantity == 18


def test_cancelled_order_cannot_be_delivered(stock_client, product, supplier):
    order = make_supply_order(product, supplier, quantity=5)
    cancel(stock_client, order)

    response = deliver(stock_client, order)

    assert response.status_code == 400
    assert order.status == "Cancelled"
    assert product.quantity == 10


def test_delivered_order_cannot_be_cancelled(stock_client, product, supplier):
    order = make_supply_order(product, supplier, quantity=5)
    deliver(stock_client, order)

    response = cancel(stock_client, order)

    assert response.status_code == 400
    assert order.status == "Delivered"
    assert product.quantity == 15


def test_sale_and_delivery_add_up(stock_client, customer, product, supplier):
    # Stock starts at 10. A sale takes 4 and a delivery adds 5.
    sale = stock_client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": product.id,
        "quantity": 4,
    }).get_json()
    stock_client.patch("/api/fulfil_customer_order/" + str(sale["id"]))

    order = make_supply_order(product, supplier, quantity=5)
    deliver(stock_client, order)

    assert product.quantity == 11