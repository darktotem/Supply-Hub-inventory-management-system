
import pytest

from app import app
from extensions import db
from models.inventory import Inventory


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            yield client

        db.session.remove()
        db.drop_all()



def test_create_inventory(client):
    response = client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    assert response.status_code == 201
    assert response.json["product_name"] == "Cooking Oil"
    assert response.json["quantity"] == 50


def test_get_all_inventory(client):
    client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    response = client.get("/api/inventory")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["product_name"] == "Cooking Oil"


def test_get_one_inventory(client):
    create_response = client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    item_id = create_response.json["id"]

    response = client.get(f"/api/inventory/{item_id}")

    assert response.status_code == 200
    assert response.json["id"] == item_id
    assert response.json["product_name"] == "Cooking Oil"


def test_update_inventory(client):
    create_response = client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    item_id = create_response.json["id"]

    response = client.put(f"/api/inventory/{item_id}", json={
        "quantity": 30,
        "price": 400
    })

    assert response.status_code == 200
    assert response.json["quantity"] == 30
    assert response.json["price"] == 400


def test_delete_inventory(client):
    create_response = client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    item_id = create_response.json["id"]

    response = client.delete(f"/api/inventory/{item_id}")

    assert response.status_code == 200
    assert response.json["message"] == "Inventory item deleted successfully"

    # Confirm the item no longer exists
    get_response = client.get(f"/api/inventory/{item_id}")
    assert get_response.status_code == 404


def test_get_low_stock(client):
    client.post("/api/inventory", json={
        "product_name": "Sugar",
        "category": "Food",
        "quantity": 5,
        "threshold": 10,
        "price": 180
    })

    client.post("/api/inventory", json={
        "product_name": "Cooking Oil",
        "category": "Food",
        "quantity": 50,
        "threshold": 10,
        "price": 350
    })

    response = client.get("/api/inventory/low-stock")

    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]["product_name"] == "Sugar"
