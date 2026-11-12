import random
from faker import Faker
from app import app
from extensions import db
from models import User, Role, Product, Supplier, Customer

fake = Faker()

DEV_PASSWORD = "Password123"

USERS = [
    # name, username, role, must_change_password
    ("IT Admin",            "it_admin",    Role.IT_ADMIN,            True),   # ChangeMe123
    ("Operations Director", "director",    Role.OPERATIONS_DIRECTOR, False),
    ("Procurement Officer", "procurement", Role.PROCUREMENT,         False),
    ("Store Worker",        "warehouse",   Role.STORE_WORKER,        False),
    ("Sales Officer",       "sales",       Role.SALES,               False),
    ("Finance Officer",     "finance",     Role.FINANCE,             False),
    ("Auditor",             "auditor",     Role.AUDITOR,             False),
]

CATEGORIES = ["Beverages", "Snacks", "Dairy", "Household", "Grains"]

with app.app_context():
    for name, username, role, must_change in USERS:
        if User.query.filter_by(username=username).first():
            continue
        user = User(name=name, username=username, role=role,
                    must_change_password=must_change)
        user.set_password("ChangeMe123" if username == "it_admin" else DEV_PASSWORD)
        db.session.add(user)
    db.session.commit()

    procurement = User.query.filter_by(username="procurement").first()
    sales = User.query.filter_by(username="sales").first()

    if Product.query.count() == 0:
        for i in range(1, 21):
            cost = random.randint(50, 800)
            db.session.add(Product(
                sku=f"SKU-{i:04d}",
                name=fake.unique.word().title(),
                category=random.choice(CATEGORIES),
                unit="pcs",
                cost_price=cost,
                selling_price=round(cost * 1.3, 2),
                quantity=random.randint(0, 200),
                min_threshold=random.randint(10, 30),
            ))

    if Supplier.query.count() == 0:
        for i in range(1, 6):
            db.session.add(Supplier(
                code=f"SUP-{i:04d}",
                name=fake.company(),
                contact_person=fake.name(),
                email=fake.company_email(),
                phone=fake.phone_number()[:30],
                city=fake.city(),
                country="Kenya",
                created_by=procurement.id,
            ))

    if Customer.query.count() == 0:
        for _ in range(8):
            db.session.add(Customer(
                name=fake.company(),
                email=fake.company_email(),
                phone=fake.phone_number()[:30],
                address=fake.address().replace("\n", ", ")[:255],
                created_by=sales.id,
            ))

    db.session.commit()
    print("Seeded.")
    print("  it_admin / ChangeMe123  (must change password on first login)")
    print(f"  director, procurement, warehouse, sales, finance, auditor / {DEV_PASSWORD}")