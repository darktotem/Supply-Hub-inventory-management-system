from models.customer import Customer
from models.inventory import Inventory

def invoice_payload(sales_data, **overrides):
    payload = {
        "customer_id": sales_data["customer"].id,
        "product_id": sales_data["product"].id,
        "sale_id": sales_data["sale"].id,
        "quantity": 2,
        "unit_price": "100.00",
    }

    payload.update(overrides)
    return payload


def test_create_invoice_successfully(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data),
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Invoice created successfully"
    assert data["invoice"]["quantity"] == 2
    assert data["invoice"]["total"] == "200.00"
    assert data["invoice"]["status"] == "pending"


def test_get_all_invoices(client, invoice):
    response = client.get("/invoices/")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["id"] == invoice.id


def test_create_invoice_without_json(client):
    response = client.post(
        "/invoices/",
        data="invalid json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_invoice_with_missing_fields(client):
    response = client.post(
        "/invoices/",
        json={"quantity": 2},
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_create_invoice_with_zero_quantity(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data, quantity=0),
    )

    assert response.status_code == 400


def test_create_invoice_with_negative_unit_price(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data, unit_price="-100.00"),
    )

    assert response.status_code == 400


def test_create_invoice_with_nonexistent_customer(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data, customer_id=9999),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Customer not found"


def test_create_invoice_with_nonexistent_product(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data, product_id=9999),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Product not found"


def test_create_invoice_with_nonexistent_sale(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data, sale_id=9999),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Sale not found"


def test_invoice_customer_must_match_sale(client, sales_data, database):
    another_customer = Customer(
        customer_name="Jane Doe",
        contact="0798765432",
    )

    database.session.add(another_customer)
    database.session.commit()

    response = client.post(
        "/invoices/",
        json=invoice_payload(
            sales_data,
            customer_id=another_customer.id,
        ),
    )

    assert response.status_code == 422
    assert "does not match the sale" in response.get_json()["error"]


def test_invoice_product_must_match_sale(client, sales_data, database):
    another_product = Inventory(
        product_name="Keyboard",
        category="Electronics",
        quantity=20,
        threshold=5,
        price=50.00,
    )

    database.session.add(another_product)
    database.session.commit()

    response = client.post(
        "/invoices/",
        json=invoice_payload(
            sales_data,
            product_id=another_product.id,
        ),
    )

    assert response.status_code == 422
    assert "does not match the sale" in response.get_json()["error"]


def test_invoice_total_must_match_quantity_times_unit_price(
    client,
    sales_data,
):
    response = client.post(
        "/invoices/",
        json=invoice_payload(
            sales_data,
            total="500.00",
        ),
    )

    assert response.status_code == 422
    assert "Total does not match" in response.get_json()["error"]


def test_invoice_quantity_cannot_exceed_sale_quantity(
    client,
    sales_data,
):
    response = client.post(
        "/invoices/",
        json=invoice_payload(
            sales_data,
            quantity=11,
        ),
    )

    assert response.status_code == 422
    assert "quantity" in response.get_json()["error"]


def test_invoice_total_cannot_exceed_sale_total(client, sales_data):
    response = client.post(
        "/invoices/",
        json=invoice_payload(
            sales_data,
            quantity=10,
            unit_price="101.00",
        ),
    )

    assert response.status_code == 422
    assert "sale total" in response.get_json()["error"]


def test_invoice_creation_creates_audit_log(
    client,
    sales_data,
    database,
):
    from models.audit import AuditLog

    response = client.post(
        "/invoices/",
        json=invoice_payload(sales_data),
    )

    assert response.status_code == 201

    audit = AuditLog.query.filter_by(
        entity="invoice",
        action="create",
    ).first()

    assert audit is not None
    assert audit.new_values["total"] == "200.00"
