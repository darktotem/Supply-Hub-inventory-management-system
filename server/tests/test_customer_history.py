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