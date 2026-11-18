
from app import app
from extensions import db
from models import User, Role

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

    db.session.commit()

    print(f"\nSuccessfully created {created} users.")
    print("\nTEST ACCOUNT CREDENTIALS:")
    print("IT Admin: it_admin / ChangeMe123")
    print("Director: director / Password123")
    print("Procurement: procurement / Password123")
    print("Warehouse: warehouse / Password123")
    print("Sales: sales / Password123")
    print("Finance: finance / Password123")
    print("Auditor: auditor / Password123")
