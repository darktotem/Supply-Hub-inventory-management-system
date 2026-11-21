
from app import app
from extensions import db
from models import User


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

    print("Creation of the Initial admin")

    existing_user = User.query.filter_by(username="it_admin").first()

    if existing_user:
        print(f"An Admin already exists. Please login")
        exit()

    user = User(
        name="Supply Hub [change this]",
        username="testAdmin",
        email= "initialemail@gmail.com",
        role="it_admin",
        is_active=True,
        must_change_password=True
    )

    password = "must_change_password" 
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    print(f"\nSuccessfully created the initial admin of this system")
    print("""\nTEST ACCOUNT CREDENTIALS ;
            >>>> Username ---> testAdmin
            >>>> Password ---> must_change_password
            >>>> Role  -----> It Admin
    
    """)

