
from decimal import Decimal

from models.invoice import Payment


def payment_payload(**overrides):
    payload = {
        "amount": "50.00",
        "method": "mpesa",
        "reference": "MPESA-TEST-001",
    }

    payload.update(overrides)
    return payload


def test_record_payment_successfully(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(),
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Payment recorded"
    assert data["payment"]["amount"] == "50.00"
    assert data["invoice"]["amount_paid"] == "50.00"
    assert data["invoice"]["status"] == "partial"


def test_get_payments_for_invoice(client, invoice, database):
    payment = Payment(
        invoice_id=invoice.id,
        amount=Decimal("50.00"),
        method="cash",
        reference="CASH-TEST-001",
    )

    database.session.add(payment)
    database.session.commit()

    response = client.get(
        f"/invoices/{invoice.id}/payments"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert len(data) == 1
    assert data[0]["amount"] == "50.00"


def test_get_payments_for_nonexistent_invoice(client):
    response = client.get("/invoices/9999/payments")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Invoice not found"


def test_record_payment_for_nonexistent_invoice(client):
    response = client.post(
        "/invoices/9999/payments",
        json=payment_payload(),
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Invoice not found"


def test_record_full_payment(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="200.00",
            reference="FULL-PAYMENT-001",
        ),
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["invoice"]["amount_paid"] == "200.00"
    assert data["invoice"]["status"] == "paid"


def test_record_multiple_partial_payments(client, invoice):
    first_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="50.00",
            reference="PARTIAL-001",
        ),
    )

    second_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="100.00",
            reference="PARTIAL-002",
        ),
    )

    assert first_payment.status_code == 201
    assert second_payment.status_code == 201

    data = second_payment.get_json()

    assert data["invoice"]["amount_paid"] == "150.00"
    assert data["invoice"]["status"] == "partial"


def test_payment_cannot_exceed_balance_due(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(amount="250.00"),
    )

    assert response.status_code == 422
    assert "exceeds the balance due" in response.get_json()["error"]


def test_payment_cannot_be_zero(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(amount="0.00"),
    )

    assert response.status_code == 400


def test_payment_cannot_be_negative(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(amount="-10.00"),
    )

    assert response.status_code == 400


def test_payment_with_invalid_method(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(method="bitcoin"),
    )

    assert response.status_code == 400


def test_payment_without_json(client, invoice):
    response = client.post(
        f"/invoices/{invoice.id}/payments",
        data="invalid json",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_cannot_pay_already_paid_invoice(client, invoice):
    first_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="200.00",
            reference="PAID-INVOICE-001",
        ),
    )

    assert first_payment.status_code == 201

    second_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="10.00",
            reference="PAID-INVOICE-002",
        ),
    )

    assert second_payment.status_code == 409
    assert "already paid" in second_payment.get_json()["error"]


def test_cannot_pay_void_invoice(client, invoice, database):
    invoice.status = "void"
    database.session.commit()

    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(),
    )

    assert response.status_code == 409
    assert "already void" in response.get_json()["error"]


def test_duplicate_payment_reference_returns_conflict(
    client,
    invoice,
):
    first_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(reference="DUPLICATE-001"),
    )

    second_payment = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            amount="30.00",
            reference="DUPLICATE-001",
        ),
    )

    assert first_payment.status_code == 201
    assert second_payment.status_code == 409


def test_payment_creates_audit_log(client, invoice, database):
    from models.audit import AuditLog

    response = client.post(
        f"/invoices/{invoice.id}/payments",
        json=payment_payload(
            reference="AUDIT-PAYMENT-001",
        ),
    )

    assert response.status_code == 201

    audit = AuditLog.query.filter_by(
        entity="invoice",
        action="payment",
    ).first()

    assert audit is not None
    assert audit.new_values["payment_amount"] == "50.00"
