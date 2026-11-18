
import pytest


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def inventory_payload(**overrides):
    """Generate a valid inventory payload for testing."""

    data = {
        "product_name": "Laptop",
        "category": "Electronics",
        "quantity": 50,
        "threshold": 10,
        "price": 75000.00
    }

    data.update(overrides)
    return data


def create_inventory(client, **overrides):
    """Create an inventory item through the API."""

    return client.post(
        "/inventory",
        json=inventory_payload(**overrides)
    )


# --------------------------------------------------
# 1. CREATE INVENTORY TESTS
# --------------------------------------------------

def test_create_inventory_successfully(client, database):
    response = create_inventory(client)

    assert response.status_code == 201

    data = response.get_json()

    assert data["product_name"] == "Laptop"
    assert data["category"] == "Electronics"
    assert data["quantity"] == 50
    assert data["threshold"] == 10
    assert data["price"] == 75000.00
    assert "id" in data


def test_create_inventory_missing_request_body(client, database):
    response = client.post("/inventory")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Request body is required"


def test_create_inventory_missing_required_fields(client, database):
    response = client.post(
        "/inventory",
        json={"product_name": "Laptop"}
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_inventory_negative_quantity(client, database):
    response = create_inventory(client, quantity=-5)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_inventory_negative_threshold(client, database):
    response = create_inventory(client, threshold=-1)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_inventory_negative_price(client, database):
    response = create_inventory(client, price=-100)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_inventory_empty_product_name(client, database):
    response = create_inventory(client, product_name="")

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_inventory_product_name_too_long(client, database):
    response = create_inventory(client, product_name="A" * 151)

    assert response.status_code == 400
    assert "errors" in response.get_json()


# --------------------------------------------------
# 2. GET INVENTORY TESTS
# --------------------------------------------------

def test_get_all_inventory(client, database):
    create_inventory(client)
    create_inventory(
        client,
        product_name="Mouse",
        category="Accessories",
        quantity=30,
        threshold=5,
        price=1500
    )

    response = client.get("/inventory")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2
    assert data[0]["product_name"] == "Laptop"
    assert data[1]["product_name"] == "Mouse"


def test_get_single_inventory_item(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    response = client.get(f"/inventory/{item_id}")

    assert response.status_code == 200

    data = response.get_json()

    assert data["id"] == item_id
    assert data["product_name"] == "Laptop"


def test_get_nonexistent_inventory_item(client, database):
    response = client.get("/inventory/9999")

    assert response.status_code == 404

    assert response.get_json()["error"] == "Inventory item not found"


# --------------------------------------------------
# 3. UPDATE INVENTORY TESTS
# --------------------------------------------------

def test_update_inventory_successfully(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    updated_data = inventory_payload(
        product_name="HP EliteBook",
        quantity=40,
        price=85000
    )

    response = client.put(
        f"/inventory/{item_id}",
        json=updated_data
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["product_name"] == "HP EliteBook"
    assert data["quantity"] == 40
    assert data["price"] == 85000


def test_update_inventory_partially(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    response = client.put(
        f"/inventory/{item_id}",
        json={"quantity": 25}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["quantity"] == 25

    # Other fields should remain unchanged
    assert data["product_name"] == "Laptop"
    assert data["category"] == "Electronics"
    assert data["threshold"] == 10
    assert data["price"] == 75000.00


def test_update_inventory_with_invalid_quantity(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    response = client.put(
        f"/inventory/{item_id}",
        json={"quantity": -10}
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_update_inventory_missing_request_body(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    response = client.put(f"/inventory/{item_id}")

    assert response.status_code == 400

    assert response.get_json()["error"] == "Request body is required"


def test_update_nonexistent_inventory_item(client, database):
    response = client.put(
        "/inventory/9999",
        json={"quantity": 20}
    )

    assert response.status_code == 404


# --------------------------------------------------
# 4. DELETE INVENTORY TESTS
# --------------------------------------------------

def test_delete_inventory_successfully(client, database):
    created = create_inventory(client)

    item_id = created.get_json()["id"]

    response = client.delete(f"/inventory/{item_id}")

    assert response.status_code == 200

    assert response.get_json()["message"] == (
        "Inventory item deleted successfully"
    )

    # Confirm that the item no longer exists
    check = client.get(f"/inventory/{item_id}")

    assert check.status_code == 404


def test_delete_nonexistent_inventory_item(client, database):
    response = client.delete("/inventory/9999")

    assert response.status_code == 404


# --------------------------------------------------
# 5. LOW STOCK TESTS
# --------------------------------------------------

def test_get_low_stock_inventory(client, database):
    # Quantity below threshold
    create_inventory(
        client,
        product_name="Keyboard",
        quantity=3,
        threshold=10
    )

    # Quantity equal to threshold
    create_inventory(
        client,
        product_name="Mouse",
        quantity=10,
        threshold=10
    )

    # Quantity above threshold
    create_inventory(
        client,
        product_name="Monitor",
        quantity=50,
        threshold=10
    )

    response = client.get("/inventory/low-stock")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2

    product_names = [item["product_name"] for item in data]

    assert "Keyboard" in product_names
    assert "Mouse" in product_names
    assert "Monitor" not in product_names


def test_get_low_stock_when_inventory_is_empty(client, database):
    response = client.get("/inventory/low-stock")

    assert response.status_code == 200

    assert response.get_json() == []


# --------------------------------------------------
# 6. SEARCH INVENTORY TESTS
# --------------------------------------------------

def test_search_inventory_by_product_name(client, database):
    create_inventory(client, product_name="HP Laptop")

    create_inventory(
        client,
        product_name="Dell Laptop",
        category="Electronics"
    )

    response = client.post(
        "/inventory/search",
        json={"product_name": "HP Laptop"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["product_name"] == "HP Laptop"


def test_search_inventory_partial_product_name(client, database):
    create_inventory(client, product_name="HP EliteBook")

    create_inventory(
        client,
        product_name="HP ProBook"
    )

    response = client.post(
        "/inventory/search",
        json={"product_name": "HP"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 2


def test_search_inventory_case_insensitive(client, database):
    create_inventory(client, product_name="HP EliteBook")

    response = client.post(
        "/inventory/search",
        json={"product_name": "hp"}
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["product_name"] == "HP EliteBook"


def test_search_inventory_no_matches(client, database):
    create_inventory(client)

    response = client.post(
        "/inventory/search",
        json={"product_name": "Samsung"}
    )

    assert response.status_code == 200

    assert response.get_json() == []


def test_search_inventory_missing_request_body(client, database):
    response = client.post("/inventory/search")

    assert response.status_code == 400

    assert response.get_json()["error"] == "Request body is required"


def test_search_inventory_missing_product_name(client, database):
    response = client.post(
        "/inventory/search",
        json={}
    )

    assert response.status_code == 400

    assert "errors" in response.get_json()


def test_search_inventory_empty_product_name(client, database):
    response = client.post(
        "/inventory/search",
        json={"product_name": ""}
    )

    assert response.status_code == 400

    assert "errors" in response.get_json()
