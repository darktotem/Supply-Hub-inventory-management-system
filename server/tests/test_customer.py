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