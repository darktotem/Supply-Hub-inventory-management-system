
import pytest

from models.user import Role, User


PASSWORD = "TestPassword123!"


# --------------------------------------------------
# LOGIN TESTS
# --------------------------------------------------

def test_login_successful(client, user_factory):
    user_factory(
        role=Role.SALES,
        username="sales_test"
    )

    response = client.post(
        "/api/login",
        json={
            "username": "sales_test",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert "token" in data
    assert data["token"]

    assert data["user"]["username"] == "sales_test"
    assert data["user"]["role"] == Role.SALES
    assert data["user"]["is_active"] is True


def test_login_with_incorrect_password(client, user_factory):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "username": "sales_test",
            "password": "WrongPassword123!"
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_with_nonexistent_username(client):
    response = client.post(
        "/api/login",
        json={
            "username": "unknown_user",
            "password": PASSWORD
        }
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_with_inactive_account(client, user_factory):
    user_factory(
        username="inactive_user",
        is_active=False
    )

    response = client.post(
        "/api/login",
        json={
            "username": "inactive_user",
            "password": PASSWORD
        }
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Access denied. Contact IT."


def test_login_normalizes_username(client, user_factory):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "username": "  SALES_TEST  ",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "sales_test"


def test_login_missing_username(client, user_factory):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "password": PASSWORD
        }
    )

    assert response.status_code == 400


def test_login_missing_password(client, user_factory):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "username": "sales_test"
        }
    )

    assert response.status_code == 400


def test_login_does_not_expose_sensitive_user_data(
    client, user_factory
):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "username": "sales_test",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200

    user_data = response.get_json()["user"]

    forbidden_fields = {
        "password",
        "password_hash",
        "recovery_code_hash",
        "recovery_code_expires",
        "recovery_attempts"
    }

    assert forbidden_fields.isdisjoint(user_data.keys())


def test_login_uses_case_normalized_username(client, user_factory):
    user_factory(username="sales_test")

    response = client.post(
        "/api/login",
        json={
            "username": "SALES_TEST",
            "password": PASSWORD
        }
    )

    assert response.status_code == 200
