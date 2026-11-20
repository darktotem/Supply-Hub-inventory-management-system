from datetime import datetime, timedelta

from app import app
from extensions import db
from models import User, Role, Inventory
from models.customer import Customer
from models.customer_history import CustomerHistory
from utils.stock import take_stock

DEV_PASSWORD = "Password123"

USERS = [
    ("IT Admin", "it_admin", Role.IT_ADMIN, True),
    ("Operations Director", "director", Role.OPERATIONS_DIRECTOR, False),
    ("Procurement Officer", "procurement", Role.PROCUREMENT, False),
    ("Store Worker", "warehouse", Role.STORE_WORKER, False),
    ("Sales Officer", "sales", Role.SALES, False),
    ("Finance Officer", "finance", Role.FINANCE, False),
    ("Auditor", "auditor", Role.AUDITOR, False),
]

INVENTORY_ITEMS = [
    {
        "product_name": "HP EliteBook 840",
        "category": "Electronics",
        "quantity": 25,
        "threshold": 5,
        "price": 85000.00,
    },
    {
        "product_name": "Dell Latitude 5420",
        "category": "Electronics",
        "quantity": 15,
        "threshold": 5,
        "price": 75000.00,
    },
    {
        "product_name": "Wireless Mouse",
        "category": "Accessories",
        "quantity": 50,
        "threshold": 10,
        "price": 1200.00,
    },
    {
        "product_name": "Mechanical Keyboard",
        "category": "Accessories",
        "quantity": 20,
        "threshold": 5,
        "price": 3500.00,
    },
    {
        "product_name": "HP LaserJet Printer",
        "category": "Printers",
        "quantity": 8,
        "threshold": 3,
        "price": 32000.00,
    },
    {
        "product_name": "USB Flash Drive 64GB",
        "category": "Storage",
        "quantity": 4,
        "threshold": 10,
        "price": 1500.00,
    },
]

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


with app.app_context():
    created = 0
    products_created = 0

    for name, username, role, must_change in USERS:
        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            print(f"Already exists: {username}")
            continue

        user = User(
            name=name,
            username=username,
            role=role,
            must_change_password=must_change,
        )

        password = "ChangeMe123" if username == "it_admin" else DEV_PASSWORD
        user.set_password(password)

        db.session.add(user)
        created += 1

    for item in INVENTORY_ITEMS:
        existing_product = Inventory.query.filter_by(
            product_name=item["product_name"]
        ).first()

        if existing_product:
            print(f"Already exists: {item['product_name']}")
            continue

        product = Inventory(**item)
        db.session.add(product)
        products_created += 1

    db.session.commit()

    print(f"\nSuccessfully created {created} users.")
    print(f"Successfully created {products_created} products.")

    seed_customers()
    seed_orders()

    print("\nTEST ACCOUNT CREDENTIALS:")
    print("IT Admin: it_admin / ChangeMe123")
    print("Director: director / Password123")
    print("Procurement: procurement / Password123")
    print("Warehouse: warehouse / Password123")
    print("Sales: sales / Password123")
    print("Finance: finance / Password123")
    print("Auditor: auditor / Password123")