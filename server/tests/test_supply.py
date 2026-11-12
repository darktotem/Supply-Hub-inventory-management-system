import pytest

from app import app
from extensions import db
from datetime import date
from models.supplier import Supplier
from models.supply_history import SupplyHistory
from models.inventory import Inventory
from controllers.supply import supply_bp

if "supply" not in app.blueprints:
    app.register_blueprint(supply_bp)


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_create_supplier(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    db.session.add(supplier)
    db.session.commit()

    assert supplier.id is not None
    assert supplier.name == "ABC Suppliers"
    assert supplier.email == "abc@gmail.com"

def test_supplier_to_dict(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    db.session.add(supplier)
    db.session.commit()

    result = supplier.to_dict()

    assert result["id"] == supplier.id
    assert result["name"] == "ABC Suppliers"
    assert result["contact_person"] == "John"
    assert result["phone"] == "0712345678"
    assert result["email"] == "abc@gmail.com"
    assert result["address"] == "Nairobi"

def test_create_supply_history(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    product = Inventory(
        product_name="Cooking Oil",
        category="Food",
        quantity=50,
        threshold=10,
        price=350
    )

    db.session.add(supplier)
    db.session.add(product)
    db.session.commit()

    supply = SupplyHistory(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=20,
        date_of_order=date(2026, 11, 12)
    )

    db.session.add(supply)
    db.session.commit()

    assert supply.id is not None
    assert supply.product_id == product.id
    assert supply.supplier_id == supplier.id
    assert supply.quantity == 20

def test_supply_history_to_dict(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    product = Inventory(
        product_name="Cooking Oil",
        category="Food",
        quantity=50,
        threshold=10,
        price=350
    )

    db.session.add(supplier)
    db.session.add(product)
    db.session.commit()

    supply = SupplyHistory(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=20,
        date_of_order=date(2026, 11, 12)
    )

    db.session.add(supply)
    db.session.commit()

    result = supply.to_dict()

    assert result["id"] == supply.id
    assert result["product_id"] == product.id
    assert result["supplier_id"] == supplier.id
    assert result["quantity"] == 20
    assert result["date_of_order"] == "2026-11-12"
    assert result["status"] == "Pending"
    assert result["supplier"]["name"] == "ABC Suppliers"

def test_register_supplier(client):
    response = client.post("/register_supplier", json={
        "name": "ABC Suppliers",
        "contact_person": "John",
        "phone": "0712345678",
        "email": "abc@gmail.com",
        "address": "Nairobi"
    })

    assert response.status_code == 201
    assert response.json["name"] == "ABC Suppliers"
    assert response.json["email"] == "abc@gmail.com"

def test_get_supply_history(client):
    response = client.get("/supplyhistory")

    assert response.status_code == 200
    assert response.json == []

def test_delete_supplier(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    db.session.add(supplier)
    db.session.commit()

    response = client.delete(f"/delete_suppliers/{supplier.id}")

    assert response.status_code == 200
    assert response.json["message"] == "Supplier deleted successfully"

    deleted_supplier = db.session.get(Supplier, supplier.id)
    assert deleted_supplier is None

def test_create_supply_order(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    product = Inventory(
        product_name="Cooking Oil",
        category="Food",
        quantity=50,
        threshold=10,
        price=350
    )

    db.session.add(supplier)
    db.session.add(product)
    db.session.commit()

    response = client.post("/supply_orders", json={
        "product_id": product.id,
        "supplier_id": supplier.id,
        "quantity": 20,
        "date_of_order": "2026-11-12"
    })

    assert response.status_code == 201
    assert response.json["product_id"] == product.id
    assert response.json["supplier_id"] == supplier.id
    assert response.json["quantity"] == 20
    assert response.json["status"] == "Pending"

def test_cancel_supply_order(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    product = Inventory(
        product_name="Cooking Oil",
        category="Food",
        quantity=50,
        threshold=10,
        price=350
    )

    db.session.add(supplier)
    db.session.add(product)
    db.session.commit()

    supply = SupplyHistory(
        product_id=product.id,
        supplier_id=supplier.id,
        quantity=20,
        date_of_order=date(2026, 11, 12)
    )

    db.session.add(supply)
    db.session.commit()

    response = client.patch(
        f"/cancel_order/{supply.id}",
        json={"status": "Cancelled"}
    )

    assert response.status_code == 200
    assert response.json["message"] == "Supply order cancelled successfully"

    db.session.refresh(supply)
    assert supply.status == "Cancelled"


def test_register_duplicate_supplier(client):
    supplier_data = {
        "name": "ABC Suppliers",
        "contact_person": "John",
        "phone": "0712345678",
        "email": "abc@gmail.com",
        "address": "Nairobi"
    }

    first_response = client.post(
        "/register_supplier",
        json=supplier_data
    )

    second_response = client.post(
        "/register_supplier",
        json=supplier_data
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json["error"] == "Supplier with this email already exists"

def test_create_supply_order_with_invalid_product(client):
    supplier = Supplier(
        name="ABC Suppliers",
        contact_person="John",
        phone="0712345678",
        email="abc@gmail.com",
        address="Nairobi"
    )

    db.session.add(supplier)
    db.session.commit()

    response = client.post("/supply_orders", json={
        "product_id": 999,
        "supplier_id": supplier.id,
        "quantity": 20,
        "date_of_order": "2026-11-12"
    })

    assert response.status_code == 404
    assert response.json["error"] == "Product not found"

