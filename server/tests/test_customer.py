import pytest
from sqlalchemy.exc import IntegrityError
from extensions import db
from models.customer import Customer


def test_create_customer(app):
    customer = Customer(customer_name="Brian Otieno", contact="0723456789")
    db.session.add(customer)
    db.session.commit()

    assert customer.id is not None
    assert customer.customer_name == "Brian Otieno"
    assert customer.contact == "0723456789"


def test_customer_to_dict(customer):
    data = customer.to_dict()

    assert data == {
        "id": customer.id,
        "customer_name": "Amina Wanjiru",
        "contact": "0712345678",
    }


def test_customer_name_is_required(app):
    customer = Customer(contact="0723456789")
    db.session.add(customer)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()
=======

# tests/test_customers.py

# --------------------------------------------------
# HELPER
# --------------------------------------------------

def register_customer(client, headers, **overrides):
    data = {
        "customer_name": "Jane Doe",
        "contact": "0712345678",
    }

    data.update(overrides)

    return client.post(
        "/api/register_customer",
        json=data,
        headers=headers
    )


# --------------------------------------------------
# 1. CUSTOMER REGISTRATION
# --------------------------------------------------

def test_register_customer_successfully(client, database, sales_user):
    response = register_customer(client, sales_user["headers"])

    assert response.status_code == 201

    data = response.get_json()

    assert data["customer_name"] == "Jane Doe"
    assert data["contact"] == "0712345678"
    assert "id" in data


def test_register_customer_as_operations_director(
    client, database, operations_user
):
    response = register_customer(
        client,
        operations_user["headers"]
    )

    assert response.status_code == 201


def test_register_customer_without_authentication(client, database):
    response = client.post(
        "/api/register_customer",
        json={
            "customer_name": "Jane Doe",
            "contact": "0712345678"
        }
    )

    assert response.status_code == 401


def test_register_customer_with_unauthorized_role(
    client, database, it_admin_user
):
    response = register_customer(
        client,
        it_admin_user["headers"]
    )

    assert response.status_code == 403


def test_register_customer_with_inactive_user(
    client, database, inactive_sales_user
):
    response = register_customer(
        client,
        inactive_sales_user["headers"]
    )

    assert response.status_code == 401


def test_register_customer_missing_customer_name(
    client, database, sales_user
):
    response = register_customer(
        client,
        sales_user["headers"],
        customer_name=None
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_register_customer_missing_contact(
    client, database, sales_user
):
    response = client.post(
        "/api/register_customer",
        json={"customer_name": "Jane Doe"},
        headers=sales_user["headers"]
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_register_customer_empty_name(client, database, sales_user):
    response = register_customer(
        client,
        sales_user["headers"],
        customer_name=""
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_register_customer_invalid_phone_number(
    client, database, sales_user
):
    response = register_customer(
        client,
        sales_user["headers"],
        contact="invalid-phone"
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_register_customer_phone_number_too_short(
    client, database, sales_user
):
    response = register_customer(
        client,
        sales_user["headers"],
        contact="12345"
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


# --------------------------------------------------
# 2. GET CUSTOMERS
# --------------------------------------------------

def test_get_all_customers(client, database, sales_user):
    register_customer(client, sales_user["headers"])

    register_customer(
        client,
        sales_user["headers"],
        customer_name="John Smith",
        contact="0723456789"
    )

    response = client.get(
        "/api/customers",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    names = {customer["customer_name"] for customer in data}

    assert names == {"Jane Doe", "John Smith"}


def test_get_customers_without_authentication(client, database):
    response = client.get("/api/customers")

    assert response.status_code == 401


def test_get_customers_when_empty(client, database, sales_user):
    response = client.get(
        "/api/customers",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200
    assert response.get_json() == []


# --------------------------------------------------
# 3. DELETE CUSTOMERS
# --------------------------------------------------

def test_delete_customer_successfully(client, database, sales_user):
    created = register_customer(client, sales_user["headers"])

    customer_id = created.get_json()["id"]

    response = client.delete(
        f"/api/delete_customer/{customer_id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 200

    assert response.get_json()["message"] == "Customer deleted"

    # Confirm deletion in the database
    from models.customer import Customer

    deleted_customer = database.session.get(Customer, customer_id)

    assert deleted_customer is None


def test_delete_customer_as_operations_director(
    client, database, operations_user
):
    created = register_customer(
        client,
        operations_user["headers"]
    )

    customer_id = created.get_json()["id"]

    response = client.delete(
        f"/api/delete_customer/{customer_id}",
        headers=operations_user["headers"]
    )

    assert response.status_code == 200


def test_delete_customer_with_existing_orders(
    client, database, sales_user, sales_data
):
    customer_id = sales_data["customer"].id

    response = client.delete(
        f"/api/delete_customer/{customer_id}",
        headers=sales_user["headers"]
    )

    assert response.status_code == 400

    assert response.get_json()["error"] == (
        "This customer has orders and cannot be deleted"
    )


def test_delete_nonexistent_customer(client, database, sales_user):
    response = client.delete(
        "/api/delete_customer/9999",
        headers=sales_user["headers"]
    )

    assert response.status_code == 404

    assert response.get_json()["error"] == "Customer not found"


def test_delete_customer_without_authentication(
    client, database
):
    response = client.delete("/api/delete_customer/1")

    assert response.status_code == 401


def test_delete_customer_with_unauthorized_role(
    client, database, it_admin_user, sales_user
):
    created = register_customer(
        client,
        sales_user["headers"]
    )

    customer_id = created.get_json()["id"]

    response = client.delete(
        f"/api/delete_customer/{customer_id}",
        headers=it_admin_user["headers"]
    )

    assert response.status_code == 403
