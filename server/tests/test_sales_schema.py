import pytest
from marshmallow import ValidationError
from schemas.sales_schema import CustomerSchema, OrderSchema

customer_schema = CustomerSchema()
order_schema = OrderSchema()


# ---------- CustomerSchema ----------

def test_valid_customer():
    data = customer_schema.load({"customer_name": "Amina", "contact": "0712345678"})

    assert data["customer_name"] == "Amina"
    assert data["contact"] == "0712345678"


def test_customer_missing_contact():
    with pytest.raises(ValidationError) as error:
        customer_schema.load({"customer_name": "Amina"})

    assert "contact" in error.value.messages


def test_customer_empty_name():
    with pytest.raises(ValidationError) as error:
        customer_schema.load({"customer_name": "", "contact": "0712345678"})

    assert "customer_name" in error.value.messages


def test_customer_bad_phone_number():
    with pytest.raises(ValidationError) as error:
        customer_schema.load({"customer_name": "Amina", "contact": "abc"})

    assert "contact" in error.value.messages


def test_customer_unknown_field_is_rejected():
    with pytest.raises(ValidationError) as error:
        customer_schema.load({
            "customer_name": "Amina",
            "contact": "0712345678",
            "email": "amina@example.com",
        })

    assert "email" in error.value.messages


# ---------- OrderSchema ----------

def test_valid_order():
    data = order_schema.load({"customer_id": 1, "product_id": 2, "quantity": 3})

    assert data == {"customer_id": 1, "product_id": 2, "quantity": 3}


def test_order_quantity_text_becomes_number():
    data = order_schema.load({"customer_id": 1, "product_id": 2, "quantity": "2"})

    assert data["quantity"] == 2


def test_order_quantity_zero_is_rejected():
    with pytest.raises(ValidationError) as error:
        order_schema.load({"customer_id": 1, "product_id": 2, "quantity": 0})

    assert "quantity" in error.value.messages


def test_order_missing_product():
    with pytest.raises(ValidationError) as error:
        order_schema.load({"customer_id": 1, "quantity": 2})

    assert "product_id" in error.value.messages