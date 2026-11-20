
from app import app
from extensions import db
from models import User, Role, Inventory

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

with app.app_context():
    created = 0

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

        products_created = 0

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
    print("\nTEST ACCOUNT CREDENTIALS:")
    print("IT Admin: it_admin / ChangeMe123")
    print("Director: director / Password123")
    print("Procurement: procurement / Password123")
    print("Warehouse: warehouse / Password123")
    print("Sales: sales / Password123")
    print("Finance: finance / Password123")
    print("Auditor: auditor / Password123")
