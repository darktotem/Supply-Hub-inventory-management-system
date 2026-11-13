from extensions import db


def make_order(client, customer, product, quantity=2):
    # Helper: create an order through the API and return its JSON
    response = client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": product.id,
        "quantity": quantity,
    })
    return response.get_json()


# ---------- Customers ----------

def test_get_customers_empty(client):
    response = client.get("/api/customers")

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_customers_returns_customer(client, customer):
    response = client.get("/api/customers")

    assert response.status_code == 200
    assert response.get_json()[0]["customer_name"] == "Amina Wanjiru"


def test_register_customer(client):
    response = client.post("/api/register_customer", json={
        "customer_name": "Brian Otieno",
        "contact": "0723456789",
    })

    assert response.status_code == 201
    assert response.get_json()["customer_name"] == "Brian Otieno"


def test_register_customer_invalid_data(client):
    response = client.post("/api/register_customer", json={
        "customer_name": "",
        "contact": "abc",
    })

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_delete_customer(client, customer):
    response = client.delete("/api/delete_customer/" + str(customer.id))

    assert response.status_code == 200
    assert client.get("/api/customers").get_json() == []


def test_delete_customer_not_found(client):
    response = client.delete("/api/delete_customer/999")

    assert response.status_code == 404


def test_delete_customer_with_orders_is_blocked(client, customer, product):
    make_order(client, customer, product)

    response = client.delete("/api/delete_customer/" + str(customer.id))

    assert response.status_code == 400


# ---------- Creating orders ----------

def test_create_order(client, customer, product):
    response = client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": product.id,
        "quantity": 2,
    })
    data = response.get_json()

    assert response.status_code == 201
    assert data["status"] == "pending"
    assert data["total_price"] == 700
    assert product.quantity == 10  # stock only drops when fulfilled


def test_create_order_not_enough_stock(client, customer, product):
    response = client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": product.id,
        "quantity": 11,
    })

    assert response.status_code == 400


def test_create_order_unknown_customer(client, product):
    response = client.post("/api/post_customer_orders", json={
        "customer_id": 999,
        "product_id": product.id,
        "quantity": 1,
    })

    assert response.status_code == 404


def test_create_order_unknown_product(client, customer):
    response = client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": 999,
        "quantity": 1,
    })

    assert response.status_code == 404


def test_create_order_invalid_quantity(client, customer, product):
    response = client.post("/api/post_customer_orders", json={
        "customer_id": customer.id,
        "product_id": product.id,
        "quantity": 0,
    })

    assert response.status_code == 400


def test_orders_are_listed_newest_first(client, customer, product):
    first = make_order(client, customer, product)
    second = make_order(client, customer, product)

    response = client.get("/api/customer_orders")
    orders = response.get_json()

    assert response.status_code == 200
    assert orders[0]["id"] == second["id"]
    assert orders[1]["id"] == first["id"]


# ---------- Cancelling orders ----------

def test_cancel_order(client, customer, product):
    order = make_order(client, customer, product)

    response = client.patch("/api/cancel_customer_order/" + str(order["id"]))

    assert response.status_code == 200
    assert response.get_json()["status"] == "cancelled"


def test_cancel_order_twice_is_blocked(client, customer, product):
    order = make_order(client, customer, product)
    client.patch("/api/cancel_customer_order/" + str(order["id"]))

    response = client.patch("/api/cancel_customer_order/" + str(order["id"]))

    assert response.status_code == 400


def test_cancel_order_not_found(client):
    response = client.patch("/api/cancel_customer_order/999")

    assert response.status_code == 404


# ---------- Fulfilling orders ----------

def test_fulfil_order_reduces_stock(client, customer, product):
    order = make_order(client, customer, product, quantity=2)

    response = client.patch("/api/fulfil_customer_order/" + str(order["id"]))

    assert response.status_code == 200
    assert response.get_json()["status"] == "fulfilled"
    assert product.quantity == 8


def test_fulfil_order_twice_is_blocked(client, customer, product):
    order = make_order(client, customer, product, quantity=2)
    client.patch("/api/fulfil_customer_order/" + str(order["id"]))

    response = client.patch("/api/fulfil_customer_order/" + str(order["id"]))

    assert response.status_code == 400
    assert product.quantity == 8  # stock was only reduced once


def test_fulfil_cancelled_order_is_blocked(client, customer, product):
    order = make_order(client, customer, product)
    client.patch("/api/cancel_customer_order/" + str(order["id"]))

    response = client.patch("/api/fulfil_customer_order/" + str(order["id"]))

    assert response.status_code == 400


def test_fulfil_order_when_stock_dropped(client, customer, product):
    order = make_order(client, customer, product, quantity=8)

    # Someone else used up the stock after the order was created
    product.quantity = 3
    db.session.commit()

    response = client.patch("/api/fulfil_customer_order/" + str(order["id"]))

    assert response.status_code == 400
    assert product.quantity == 3  # stock was not changed


def test_fulfil_order_not_found(client):
    response = client.patch("/api/fulfil_customer_order/999")

    assert response.status_code == 404


# ---------- Customer history ----------

def test_customer_history_empty(client):
    response = client.get("/api/customer_history")

    assert response.status_code == 200
    assert response.get_json() == []


def test_customer_history_only_shows_finished_orders(client, customer, product):
    pending = make_order(client, customer, product)
    fulfilled = make_order(client, customer, product)
    cancelled = make_order(client, customer, product)
    client.patch("/api/fulfil_customer_order/" + str(fulfilled["id"]))
    client.patch("/api/cancel_customer_order/" + str(cancelled["id"]))

    response = client.get("/api/customer_history")
    ids = [h["id"] for h in response.get_json()]

    assert response.status_code == 200
    assert pending["id"] not in ids
    assert ids == [cancelled["id"], fulfilled["id"]]  # newest first    