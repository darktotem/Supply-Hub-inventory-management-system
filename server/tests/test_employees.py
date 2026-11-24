from models.user import Role, User


def test_it_admin_can_list_and_create_employee(client, it_admin_user):
    response = client.get("/api/employees", headers=it_admin_user["headers"])
    assert response.status_code == 200

    response = client.post(
        "/api/employees",
        headers=it_admin_user["headers"],
        json={
            "name": "Test Sales",
            "username": "test_sales",
            "email": "test_sales@example.com",
            "role": Role.SALES,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["employee"]["username"] == "test_sales"
    assert data["employee"]["must_change_password"] is True
    assert data["temporary_password"]


def test_non_admin_cannot_manage_employees(client, sales_user):
    response = client.get("/api/employees", headers=sales_user["headers"])
    assert response.status_code == 403


def test_employee_update_access_reset_and_delete(client, database, it_admin_user, user_factory):
    employee = user_factory(username="employee_test", role=Role.SALES)
    employee_id = employee["user"].id

    response = client.patch(
        f"/api/employees/{employee_id}",
        headers=it_admin_user["headers"],
        json={"name": "Updated Employee", "role": Role.FINANCE},
    )
    assert response.status_code == 200

    response = client.patch(
        f"/api/employees/{employee_id}/access",
        headers=it_admin_user["headers"],
        json={"is_active": False},
    )
    assert response.status_code == 200

    response = client.post(
        f"/api/employees/{employee_id}/reset_password",
        headers=it_admin_user["headers"],
    )
    assert response.status_code == 200
    recovery = response.get_json()
    assert recovery["recovery_code"]
    assert recovery["expires_in_seconds"] == 60

    response = client.delete(
        f"/api/employees/{employee_id}",
        headers=it_admin_user["headers"],
    )
    assert response.status_code == 200
    assert database.session.get(User, employee_id) is None
