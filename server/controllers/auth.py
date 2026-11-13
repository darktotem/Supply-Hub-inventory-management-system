from flask import Blueprint
import jwt
from extensions import db
from models.user import User
from schemas.auth_schema import (LoginSchema, ChangePasswordSchema, ChangeUsernameSchema, VerifyRecoveryCodeSchema, SetNewPasswordSchema )

from utils.audit import log_action
from utils.decorators import login_required, current_user
from utils.tokens import create_token, create_reset_token, decode_reset_token
from utils.validators import load_json

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/api/login")
def login():
    data, err = load_json(LoginSchema)
    if err:
        return err

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return {"error": "Invalid username or password"}, 401
    if not user.is_active:
        return {"error": "Access denied. Contact IT."}, 403

    return {"token": create_token(user), "user": user.to_dict()}


@auth_bp.patch("/api/change_password")
@login_required
def change_password():
    data, err = load_json(ChangePasswordSchema)
    if err:
        return err

    user = current_user()
    if not user.check_password(data["old_password"]):
        return {"error": "Current password is incorrect"}, 400
    if data["new_password"] == data["old_password"]:
        return {"error": "New password must be different"}, 400

    user.set_password(data["new_password"])
    user.must_change_password = False
    user.clear_recovery_code()
    log_action("change_password", "user", user.id)
    db.session.commit()
    return {"message": "Password updated"}


@auth_bp.patch("/api/change_username")
@login_required
def change_username():
    data, err = load_json(ChangeUsernameSchema)
    if err:
        return err

    user = current_user()
    if not user.check_password(data["password"]):
        return {"error": "Password is incorrect"}, 400

    username = data["username"]
    if User.query.filter(User.username == username, User.id != user.id).first():
        return {"error": "Username already taken"}, 409

    old = user.username
    user.username = username
    log_action("change_username", "user", user.id, f"{old} -> {username}")
    db.session.commit()
    return {"user": user.to_dict()}


@auth_bp.post("/api/verify_recovery_code")
def verify_recovery_code():
    """Public. Step 2 of forgot-password: check the code IT gave the employee."""
    data, err = load_json(VerifyRecoveryCodeSchema)
    if err:
        return err

    generic = {"error": "Invalid or expired recovery code"}
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.is_active:
        return generic, 400

    if not user.verify_recovery_code(data["recovery_code"]):
        db.session.commit()          # saves the failed-attempt count
        return generic, 400

    user.clear_recovery_code()       # the code works only once
    db.session.commit()
    return {"reset_token": create_reset_token(user), "expires_in_minutes": 10}


@auth_bp.post("/api/set_new_password")
def set_new_password():
    """Public. Step 3: the employee creates and confirms their own password."""
    data, err = load_json(SetNewPasswordSchema)
    if err:
        return err

    if data["new_password"] != data["confirm_password"]:
        return {"error": "Passwords do not match"}, 400

    invalid = {"error": "Reset session is invalid. Ask IT for a new code"}
    try:
        payload = decode_reset_token(data["reset_token"])
        user = db.session.get(User, int(payload["sub"]))
    except jwt.ExpiredSignatureError:
        return {"error": "Reset session expired. Ask IT for a new code"}, 400
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return invalid, 400

    if (not user or not user.is_active
            or payload.get("pwd") != user.password_hash[-12:]):
        return invalid, 400

    user.set_password(data["new_password"])
    user.must_change_password = False
    user.clear_recovery_code()
    log_action("recover_password", "user", user.id, actor_id=user.id)
    db.session.commit()
    return {"message": "Password updated. You can now log in."}