from extensions import db
from models.customer_history import CustomerHistory


def make_order(customer, product):
    order = CustomerHistory(
        customer_id=customer.id,
        product_id=product.id,
        quantity=2,
        total_price=700,
    )
    db.session.add(order)
    db.session.commit()
    return order


def test_new_order_defaults(customer, product):
    order = make_order(customer, product)

    assert order.id is not None
    assert order.status == "pending"
    assert order.date_of_sale is not None


def test_order_relationships(customer, product):
    order = make_order(customer, product)

    assert order.customer.customer_name == "Amina Wanjiru"
    assert order.product.product_name == "Rice 2kg"


def test_order_to_dict(customer, product):
    order = make_order(customer, product)
    data = order.to_dict()

    assert data["customer_name"] == "Amina Wanjiru"
    assert data["product_name"] == "Rice 2kg"
    assert data["quantity"] == 2
    assert data["total_price"] == 700
    assert data["status"] == "pending"
    assert isinstance(data["date_of_sale"], str)
=======

# tests/test_customer_history.py

from models.customer_history import CustomerHistory
from models.inventory import Inventory


# --------------------------------------------------
# HELPER
# --------------------------------------------------

def create_order(client, headers, customer_id, product_id, quantity=5):
    return client.post(
        "/api/post_customer_orders",
        json={
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity
        },
        headers=headers
    )


# --------------------------------------------------
# 1. CREATE CUSTOMER ORDERS
# --------------------------------------------------

def test_create_customer_order_successfully(
    client, database, sales_user, sales_data
):
    customer = sales_data["customer"]
    product = sales_data["product"]

    response = create_order(
        client,
        sales_user["headers"],
        customer.id,
        product.id,
        quantity=5
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["customer_id"] == customer.id
    assert data["product_id"] == product.id
    assert data["quantity"] == 5
    assert data["total_price"] == 500.00
    assert data["status"] == "pending"


def test_create_order_as_operations_director(
    client, database, operations_user, sales_data
):
    response = create_order(
        client,
        operations_user["headers"],
        sales_data["customer"].id,
        sales_data["product"].id
    )

    assert response.status_code == 201


def test_create_order_without_authentication(
    client, database, sales_data
):
    response = client.post(
        "/api/post_customer_orders",
        json={
            "customer_id": sales_data["customer"].id,
            "product_id": sales_data["product"].id,
            "quantity": 5
        }
    )

    assert response.status_code == 401


def test_create_order_with_unauthorized_role(
    client, database, it_admin_user, sales_data
):
    response = create_order(
        client,
        it_admin_user["headers"],
        sales_data["customer"].id,
        sales_data["product"].id
    )

    assert response.status_code == 403


def test_create_order_with_nonexistent_customer(
    client, database, sales_user, sales_data
):
    response = create_order(
        client,
        sales_user["headers"],
        customer_id=9999,
        product_id=sales_data["product"].id
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Customer not found"


def test_create_order_with_nonexistent_product(
    client, database, sales_user, sales_data
):
    response = create_order(
        client,
        sales_user["headers"],
        customer_id=sales_data["customer"].id,
        product_id=9999
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Product not found"


def test_create_order_with_insufficient_stock(
    client, database, sales_user, sales_data
):
    product = sales_data["product"]

    response = create_order(
        client,
        sales_user["headers"],
        customer_id=sales_data["customer"].id,
        product_id=product.id,
        quantity=51
    )

    assert response.status_code == 400

    assert "Not enough stock" in response.get_json()["error"]


def test_create_order_with_zero_quantity(
    client, database, sales_user, sales_data
):
    response = create_order(
        client,
        sales_user["headers"],
        sales_data["customer"].id,
        sales_data["product"].id,
        quantity=0
    )

    assert response.status_code == 400

    assert "errors" in response.get_json()


def test_create_order_with_negative_quantity(
    client, database, sales_user, sales_data
):
    response = create_order(
        client,
        sales_user["headers"],
        sales_data["customer"].id,
        sales_data["product"].id,
        quantity=-5
    )

    assert response.status_code == 400

    assert "errors" in response.get_json()


def test_create_order_with_missing_fields(
    client, database, sales_user
):
    response = client.post(
        "/api/post_customer_orders",
        json={"quantity": 5},
        headers=sales_user["headers"]
    )

    assert response.status_code == 400

    assert "errors" in response.get_json()


def test_creating_order_does_not_reduce_inventory(
    client, database, sales_user, sales_data
):
    product = sales_data["product"]

    original_quantity = product.quantity

    response = create_order(
        client,
        sales_user["headers"],
        sales_data["customer"].id,
        product.id,
        quantity=5
    )

    assert response.status_code == 201

    database.session.refresh(product)

    assert product.quantity == original_quantity


# --------------------------------------------------
# 2. GET CUSTOMER ORDERS
# --------------------------------------------------

def test_get_all_customer_orders(
    client, database, sales_user, sales_data
):
    customer = sales_data["customer"]
    product = sales_data["product"]

    create_order(
        client,
        sales_user["headers"],
        customer.id,
        product.id,
        quantity=5
    )

    response = client.get(
        "/api/customer_orders",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    data = response.get_json()

    # One existing order from sales_data and one new order
    assert len(data) == 2


def test_get_customer_orders_without_authentication(
    client, database
):
    response = client.get("/api/customer_orders")

    assert response.status_code == 401


def test_get_customer_orders_when_empty(
    client, database, sales_user
):
    response = client.get(
        "/api/customer_orders",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    assert response.get_json() == []


# --------------------------------------------------
# 3. GET CUSTOMER HISTORY
# --------------------------------------------------

def test_customer_history_excludes_pending_orders(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    # Change the existing order to fulfilled
    sale.status = "fulfilled"
    database.session.commit()

    # Create another pending order
    create_order(
        client,
        sales_user["headers"],
        sales_data["customer"].id,
        sales_data["product"].id,
        quantity=5
    )

    response = client.get(
        "/api/customer_history",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["status"] == "fulfilled"


def test_customer_history_when_no_completed_orders(
    client, database, sales_user, sales_data
):
    response = client.get(
        "/api/customer_history",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    assert response.get_json() == []


def test_customer_history_without_authentication(
    client, database
):
    response = client.get("/api/customer_history")

    assert response.status_code == 401


# --------------------------------------------------
# 4. CANCEL CUSTOMER ORDERS
# --------------------------------------------------

def test_cancel_pending_order_successfully(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    response = client.patch(
        f"/api/cancel_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "cancelled"


def test_cancel_order_as_operations_director(
    client, database, operations_user, sales_data
):
    sale = sales_data["sale"]

    response = client.patch(
        f"/api/cancel_customer_order/{sale.id}",
        headers=operations_user["headers"]
    )

    assert response.status_code == 200

    assert response.get_json()["status"] == "cancelled"


def test_cancel_nonexistent_order(
    client, database, sales_user
):
    response = client.patch(
        "/api/cancel_customer_order/9999",
        headers=sales_user["headers"]
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Order not found"


def test_cancel_already_fulfilled_order(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    sale.status = "fulfilled"
    database.session.commit()

    response = client.patch(
        f"/api/cancel_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Only pending orders can be cancelled"
    )


def test_cancel_already_cancelled_order(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    sale.status = "cancelled"
    database.session.commit()

    response = client.patch(
        f"/api/cancel_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400


def test_cancel_order_without_authentication(
    client, database, sales_data
):
    response = client.patch(
        f"/api/cancel_customer_order/{sales_data['sale'].id}"
    )

    assert response.status_code == 401


def test_cancel_order_with_unauthorized_role(
    client, database, it_admin_user, sales_data
):
    response = client.patch(
        f"/api/cancel_customer_order/{sales_data['sale'].id}",
        headers=it_admin_user["headers"]
    )

    assert response.status_code == 403


# --------------------------------------------------
# 5. FULFIL CUSTOMER ORDERS
# --------------------------------------------------

def test_fulfil_pending_order_successfully(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]
    product = sales_data["product"]

    original_quantity = product.quantity

    response = client.patch(
        f"/api/fulfil_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "fulfilled"

    # Verify inventory deduction
    database.session.refresh(product)

    assert product.quantity == original_quantity - sale.quantity


def test_fulfil_order_as_operations_director(
    client, database, operations_user, sales_data
):
    sale = sales_data["sale"]

    response = client.patch(
        f"/api/fulfil_customer_order/{sale.id}",
        headers=operations_user["headers"]
    )

    assert response.status_code == 200

    assert response.get_json()["status"] == "fulfilled"


def test_fulfil_order_with_insufficient_stock(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]
    product = sales_data["product"]

    # The order requires 10 units, but only 5 are available
    product.quantity = 5
    database.session.commit()

    response = client.patch(
        f"/api/fulfil_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Not enough stock to fulfil this order"
    )

    # The order must remain pending
    database.session.refresh(sale)

    assert sale.status == "pending"

    # Stock must remain unchanged
    database.session.refresh(product)

    assert product.quantity == 5


def test_fulfil_already_fulfilled_order(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    sale.status = "fulfilled"
    database.session.commit()

    response = client.patch(
        f"/api/fulfil_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "Only pending orders can be fulfilled"
    )


def test_fulfil_cancelled_order(
    client, database, sales_user, sales_data
):
    sale = sales_data["sale"]

    sale.status = "cancelled"
    database.session.commit()

    response = client.patch(
        f"/api/fulfil_customer_order/{sale.id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400


def test_fulfil_nonexistent_order(
    client, database, sales_user
):
    response = client.patch(
        "/api/fulfil_customer_order/9999",
        headers=sales_user["headers"]
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Order not found"


def test_fulfil_order_without_authentication(
    client, database, sales_data
):
    response = client.patch(
        f"/api/fulfil_customer_order/{sales_data['sale'].id}"
    )

    assert response.status_code == 401


def test_fulfil_order_with_unauthorized_role(
    client, database, it_admin_user, sales_data
):
    response = client.patch(
        f"/api/fulfil_customer_order/{sales_data['sale'].id}",
        headers=it_admin_user["headers"]
    )

    assert response.status_code == 403
