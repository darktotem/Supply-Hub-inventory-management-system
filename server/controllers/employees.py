from flask import Blueprint, request

from extensions import db
from models.user import Role, User
from schemas.auth_schema import ChangeDetailsSchema, RegisterEmployeeSchema, UserSchema
from utils.audit import log_action
from utils.decorators import roles_required
from utils.validators import load_json

employees_bp = Blueprint("employees", __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


@employees_bp.get("/api/employees")
@roles_required(Role.IT_ADMIN)
def list_employees():
    employees = User.query.order_by(User.name.asc()).all()
    return {"employees": users_schema.dump(employees)}


@employees_bp.post("/api/employees")
@roles_required(Role.IT_ADMIN)
def register_employee():
    data, err = load_json(RegisterEmployeeSchema)
    if err:
        return err

    if User.query.filter_by(username=data["username"]).first():
        return {"error": "Username already taken"}, 409
    if data.get("email") and User.query.filter_by(email=data["email"]).first():
        return {"error": "Email already registered"}, 409

    employee = User(
        name=data["name"],
        username=data["username"],
        email=data.get("email"),
        role=data["role"],
        is_active=True,
        must_change_password=True,
    )

    temporary_password = data.get("password")
    if temporary_password:
        employee.set_password(temporary_password)
    else:
        temporary_password = employee.generate_recovery_code(hours=24)
        employee.set_password(temporary_password)

    db.session.add(employee)
    db.session.flush()
    log_action("register_employee", "user", employee.id)
    db.session.commit()

    return {
        "employee": user_schema.dump(employee),
        "temporary_password": temporary_password,
    }, 201


@employees_bp.patch("/api/employees/<int:employee_id>")
@roles_required(Role.IT_ADMIN)
def change_employee_details(employee_id):
    employee = db.session.get(User, employee_id)
    if not employee:
        return {"error": "Employee not found"}, 404

    data, err = load_json(ChangeDetailsSchema)
    if err:
        return err

    if "username" in data:
        existing = User.query.filter(User.username == data["username"], User.id != employee.id).first()
        if existing:
            return {"error": "Username already taken"}, 409
    if data.get("email"):
        existing = User.query.filter(User.email == data["email"], User.id != employee.id).first()
        if existing:
            return {"error": "Email already registered"}, 409

    for field in ("name", "username", "email", "role"):
        if field in data:
            setattr(employee, field, data[field])

    log_action("change_employee_details", "user", employee.id)
    db.session.commit()
    return {"employee": user_schema.dump(employee)}


@employees_bp.patch("/api/employees/<int:employee_id>/access")
@roles_required(Role.IT_ADMIN)
def change_employee_access(employee_id):
    employee = db.session.get(User, employee_id)
    if not employee:
        return {"error": "Employee not found"}, 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("is_active"), bool):
        return {"error": "is_active must be a boolean"}, 400

    employee.is_active = data["is_active"]
    action = "restore_employee" if employee.is_active else "deny_employee_access"
    log_action(action, "user", employee.id)
    db.session.commit()
    return {"employee": user_schema.dump(employee)}


@employees_bp.post("/api/employees/<int:employee_id>/reset_password")
@roles_required(Role.IT_ADMIN)
def reset_employee_password(employee_id):
    employee = db.session.get(User, employee_id)
    if not employee:
        return {"error": "Employee not found"}, 404

    recovery_code = employee.generate_recovery_code(hours=24)
    employee.must_change_password = True
    log_action("reset_employee_password", "user", employee.id)
    db.session.commit()
    return {"recovery_code": recovery_code}


@employees_bp.delete("/api/employees/<int:employee_id>")
@roles_required(Role.IT_ADMIN)
def delete_employee(employee_id):
    employee = db.session.get(User, employee_id)
    if not employee:
        return {"error": "Employee not found"}, 404

    db.session.delete(employee)
    log_action("delete_employee", "user", employee_id)
    db.session.commit()
    return {"message": "Employee deleted"}
