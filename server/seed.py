
from app import app
from extensions import db
from models import User


with app.app_context():
    created = 0

    print("Creation of the Initial admin")

    existing_user = User.query.filter_by(it_admin="it_admin").first()

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

