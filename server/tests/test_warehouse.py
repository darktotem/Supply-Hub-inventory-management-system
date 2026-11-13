from datetime import date

from app import app
from extensions import db
from models.inventory import Inventory
from models.supplier import Supplier
from models.supply_history import SupplyHistory


def test_create_inventory_product_via_warehouse_endpoint():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()

        with app.test_client() as client:
            response = client.post(
                "/warehouse/products",
                json={
                    "product_name": "Rice",
                    "category": "Food",
                    "quantity": 12,
                    "threshold": 5,
                    "price": 200,
                },
            )

            assert response.status_code == 201
            assert response.json["product_name"] == "Rice"
            assert response.json["quantity"] == 12

        db.session.remove()
        db.drop_all()


def test_mark_delivery_updates_stock_and_status():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()

        supplier = Supplier(
            name="Farm Fresh",
            contact_person="Jane",
            phone="0712345678",
            email="farm@example.com",
            address="Mombasa",
        )
        product = Inventory(
            product_name="Beans",
            category="Food",
            quantity=20,
            threshold=5,
            price=150,
        )
        db.session.add_all([supplier, product])
        db.session.commit()

        order = SupplyHistory(
            product_id=product.id,
            supplier_id=supplier.id,
            quantity=10,
            date_of_order=date.today(),
        )
        db.session.add(order)
        db.session.commit()

        with app.test_client() as client:
            response = client.patch(f"/warehouse/deliveries/{order.id}/deliver")

            assert response.status_code == 200
            assert response.json["message"] == "Delivery received successfully"
            assert db.session.get(Inventory, product.id).quantity == 30
            assert db.session.get(SupplyHistory, order.id).status == "Delivered"

        db.session.remove()
        db.drop_all()


def test_inventory_report_can_be_saved_and_listed():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.create_all()
        db.session.add(
            Inventory(
                product_name="Flour",
                category="Food",
                quantity=3,
                threshold=5,
                price=100,
            )
        )
        db.session.commit()

        with app.test_client() as client:
            live_response = client.get("/warehouse/reports")
            assert live_response.status_code == 200
            assert live_response.json["total_products"] == 1
            assert live_response.json["low_stock_count"] == 1
            assert live_response.json["generated_at"] is not None

            saved_response = client.post("/warehouse/reports")
            assert saved_response.status_code == 201
            assert saved_response.json["id"] is not None
            assert saved_response.json["low_stock_items"][0]["product_name"] == "Flour"

            history_response = client.get("/warehouse/reports/history")
            assert history_response.status_code == 200
            assert len(history_response.json) == 1
            assert history_response.json[0]["id"] == saved_response.json["id"]

        db.session.remove()
        db.drop_all()
