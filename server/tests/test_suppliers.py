
import pytest

from models.supplier import Supplier
from models.supply_history import SupplyHistory
from models.inventory import Inventory
from datetime import date


@pytest.fixture()
def valid_supplier_data():
    return {
        "name": "Tech Supplies Ltd",
        "contact_person": "James Mwangi",
        "phone": "0712345678",
        "email": "tech@example.com",
        "address": "Nairobi, Kenya"
    }


@pytest.fixture()
def existing_supplier(database):
    supplier = Supplier(
        name="Existing Supplies",
        contact_person="John Doe",
        phone="0723456789",
        email="existing@example.com",
        address="Kisumu, Kenya"
    )

    database.session.add(supplier)
    database.session.commit()

    return supplier


class TestRegisterSupplier:

    def test_register_supplier_success(
        self, client, procurement_user, valid_supplier_data
    ):
        response = client.post(
            "/register_supplier",
            json=valid_supplier_data,
            headers=procurement_user["headers"]
        )

        assert response.status_code == 201

        data = response.get_json()

        assert data["name"] == valid_supplier_data["name"]
        assert data["contact_person"] == valid_supplier_data["contact_person"]
        assert data["phone"] == valid_supplier_data["phone"]
        assert data["email"] == valid_supplier_data["email"]
        assert data["address"] == valid_supplier_data["address"]
        assert "id" in data

    def test_operations_director_can_register_supplier(
        self, client, operations_user, valid_supplier_data
    ):
        response = client.post(
            "/register_supplier",
            json=valid_supplier_data,
            headers=operations_user["headers"]
        )

        assert response.status_code == 201

    def test_register_supplier_requires_authentication(
        self, client, valid_supplier_data
    ):
        response = client.post(
            "/register_supplier",
            json=valid_supplier_data
        )

        assert response.status_code == 401

    def test_sales_officer_cannot_register_supplier(
        self, client, sales_user, valid_supplier_data
    ):
        response = client.post(
            "/register_supplier",
            json=valid_supplier_data,
            headers=sales_user["headers"]
        )

        assert response.status_code == 403

    def test_register_supplier_without_request_body(
        self, client, procurement_user
    ):
        response = client.post(
            "/register_supplier",
            headers=procurement_user["headers"]
        )

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "missing_field",
        ["name", "contact_person", "phone", "email", "address"]
    )
    def test_register_supplier_missing_required_field(
        self, client, procurement_user, valid_supplier_data, missing_field
    ):
        payload = valid_supplier_data.copy()
        payload.pop(missing_field)

        response = client.post(
            "/register_supplier",
            json=payload,
            headers=procurement_user["headers"]
        )

        assert response.status_code == 400

    def test_register_supplier_invalid_email(
        self, client, procurement_user, valid_supplier_data
    ):
        payload = valid_supplier_data.copy()
        payload["email"] = "not-an-email"

        response = client.post(
            "/register_supplier",
            json=payload,
            headers=procurement_user["headers"]
        )

        assert response.status_code == 400

    def test_register_supplier_duplicate_email(
        self, client, procurement_user, valid_supplier_data, existing_supplier
    ):
        payload = valid_supplier_data.copy()
        payload["email"] = existing_supplier.email

        response = client.post(
            "/register_supplier",
            json=payload,
            headers=procurement_user["headers"]
        )

        assert response.status_code == 409
        assert response.get_json()["error"] == (
            "Supplier with this email already exists"
        )


class TestDeleteSupplier:

    def test_delete_supplier_success(
        self, client, procurement_user, existing_supplier
    ):
        response = client.delete(
            f"/delete_suppliers/{existing_supplier.id}",
            headers=procurement_user["headers"]
        )

        assert response.status_code == 200
        assert response.get_json()["message"] == (
            "Supplier deleted successfully"
        )

    def test_delete_nonexistent_supplier(
        self, client, procurement_user
    ):
        response = client.delete(
            "/delete_suppliers/9999",
            headers=procurement_user["headers"]
        )

        assert response.status_code == 404

    def test_delete_supplier_requires_authentication(
        self, client, existing_supplier
    ):
        response = client.delete(
            f"/delete_suppliers/{existing_supplier.id}"
        )

        assert response.status_code == 401

    def test_sales_officer_cannot_delete_supplier(
        self, client, sales_user, existing_supplier
    ):
        response = client.delete(
            f"/delete_suppliers/{existing_supplier.id}",
            headers=sales_user["headers"]
        )

        assert response.status_code == 403

    def test_cannot_delete_supplier_with_existing_orders(
        self, client, procurement_user, database, existing_supplier
    ):
        product = Inventory(
            product_name="Laptop",
            category="Electronics",
            quantity=20,
            threshold=5,
            price=75000
        )

        database.session.add(product)
        database.session.commit()

        order = SupplyHistory(
            product_id=product.id,
            supplier_id=existing_supplier.id,
            quantity=10,
            date_of_order= date(2026, 11, 18)
        )

        database.session.add(order)
        database.session.commit()

        response = client.delete(
            f"/delete_suppliers/{existing_supplier.id}",
            headers=procurement_user["headers"]
        )

        assert response.status_code == 409
        assert response.get_json()["error"] == (
            "Cannot delete supplier with existing supply orders"
        )
