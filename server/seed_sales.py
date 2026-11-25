from datetime import datetime, timedelta

from app import app
from extensions import db
from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory
from utils.stock import take_stock

CUSTOMERS = [
    ("Amina Wanjiru", "0712345678"),
    ("Brian Otieno", "0723456789"),
    ("Grace Mwangi", "0734567890"),
    ("Peter Kamau", "0745678901"),
    ("Faith Achieng", "0756789012"),
    ("Samuel Kiprop", "0767890123"),
    ("Lucy Njeri", "0778901234"),
    ("David Mutua", "0789012345"),
    ("Mercy Chebet", "0790123456"),
    ("Kevin Odhiambo", "0701234567"),
]

# (customer number, product name, quantity, status, days ago)
ORDERS = [
    (0, "HP EliteBook 840", 2, "fulfilled", 12),
    (1, "Wireless Mouse", 10, "fulfilled", 10),
    (2, "Mechanical Keyboard", 4, "pending", 6),
    (3, "HP LaserJet Printer", 1, "cancelled", 5),
    (4, "Dell Latitude 5420", 3, "pending", 3),
    (5, "Wireless Mouse", 6, "fulfilled", 2),
    (6, "HP EliteBook 840", 1, "pending", 1),
    (7, "Mechanical Keyboard", 5, "pending", 0),
    (8, "Dell Latitude 5420", 1, "fulfilled", 8),
    (9, "Wireless Mouse", 3, "pending", 4),
]


def seed_customers():
    customers_created = 0

    for name, contact in CUSTOMERS:
        existing_customer = Customer.query.filter_by(contact=contact).first()

        if existing_customer:
            print(f"Already exists: {name}")
            continue

        db.session.add(Customer(customer_name=name, contact=contact))
        customers_created += 1

    db.session.commit()
    print(f"Successfully created {customers_created} customers.")


def seed_orders():
    if CustomerHistory.query.count() > 0:
        print("Customer orders already exist, skipping.")
        return

    orders_created = 0

    for customer_number, product_name, quantity, status, days_ago in ORDERS:
        customer = Customer.query.filter_by(contact=CUSTOMERS[customer_number][1]).first()
        product = Inventory.query.filter_by(product_name=product_name).first()

        if customer is None or product is None:
            continue

        if status == "fulfilled":
            # A fulfilled order takes its stock, like the real route does
            if not take_stock(product.id, quantity):
                continue
        elif quantity > product.quantity:
            continue

        order = CustomerHistory(
            customer_id=customer.id,
            product_id=product.id,
            quantity=quantity,
            total_price=product.price * quantity,
            status=status,
            date_of_sale=datetime.now() - timedelta(days=days_ago),
        )
        db.session.add(order)
        db.session.commit()
        orders_created += 1

    print(f"Successfully created {orders_created} customer orders.")


if __name__ == "__main__":
    with app.app_context():
        seed_customers()
        seed_orders()