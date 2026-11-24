
# from app import app
# from extensions import db
# from models import User


# INVENTORY_ITEMS = [
#     {
#         "product_name": "HP EliteBook 840",
#         "category": "Electronics",
#         "quantity": 25,
#         "threshold": 5,
#         "price": 85000.00,
#     },
#     {
#         "product_name": "Dell Latitude 5420",
#         "category": "Electronics",
#         "quantity": 15,
#         "threshold": 5,
#         "price": 75000.00,
#     },
#     {
#         "product_name": "Wireless Mouse",
#         "category": "Accessories",
#         "quantity": 50,
#         "threshold": 10,
#         "price": 1200.00,
#     },
#     {
#         "product_name": "Mechanical Keyboard",
#         "category": "Accessories",
#         "quantity": 20,
#         "threshold": 5,
#         "price": 3500.00,
#     },
#     {
#         "product_name": "HP LaserJet Printer",
#         "category": "Printers",
#         "quantity": 8,
#         "threshold": 3,
#         "price": 32000.00,
#     },
#     {
#         "product_name": "USB Flash Drive 64GB",
#         "category": "Storage",
#         "quantity": 4,
#         "threshold": 10,
#         "price": 1500.00,
#     },
# ]

# with app.app_context():
#     created = 0

#     print("Creation of the Initial admin")

#     existing_user = User.query.filter_by(username="testadmin").first()

#     if existing_user:
#         print(f"An Admin already exists. Please login")
#         exit()

#     user = User(
#         name="Supply Hub [change this]",
#         username="testadmin",
#         email= "initialemail@gmail.com",
#         role="it_admin",
#         is_active=True,
#         must_change_password=True
#     )

#     password = "must_change_password" 
#     user.set_password(password)

#     db.session.add(user)
#     db.session.commit()

#     print(f"\nSuccessfully created the initial admin of this system")
#     print("""\nTEST ACCOUNT CREDENTIALS ;
#             >>>> Username ---> testadmin
#             >>>> Password ---> must_change_password
#             >>>> Role  -----> It Admin
    
#     """)



from app import app
from extensions import db
from models import User, Inventory


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
    print("\n========== SUPPLY HUB INITIAL SEED ==========\n")

    # 1. Create initial admin only if one does not exist
    existing_user = User.query.filter_by(username="testadmin").first()

    if not existing_user:
        user = User(
            name="Supply Hub [change this]",
            username="testadmin",
            email="initialemail@gmail.com",
            role="it_admin",
            is_active=True,
            must_change_password=True
        )

        password = "must_change_password"
        user.set_password(password)

        db.session.add(user)
        print("Initial admin created.")
    else:
        print("Initial admin already exists. Skipping admin creation.")

    # 2. Seed inventory independently of admin creation
    created = 0
    skipped = 0

    for item in INVENTORY_ITEMS:
        existing_item = Inventory.query.filter_by(
            product_name=item["product_name"]
        ).first()

        if existing_item:
            print(f"Already exists: {item['product_name']}")
            skipped += 1
            continue

        inventory_item = Inventory(**item)
        db.session.add(inventory_item)

        print(f"Added: {item['product_name']}")
        created += 1

    # 3. Commit all new records
    db.session.commit()

    print("\n========== SEED SUMMARY ==========")
    print(f"Inventory products created: {created}")
    print(f"Inventory products skipped: {skipped}")
    print(f"Total inventory products: {Inventory.query.count()}")
    print(f"Total users: {User.query.count()}")

    print("\nSeed completed successfully.")

