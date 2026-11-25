from flask import Blueprint
import jwt
from extensions import db
from models.user import User
from schemas.auth_schema import (LoginSchema, 
                                 ChangePasswordSchema, 
                                 ChangeUsernameSchema, 
                                 VerifyRecoveryCodeSchema, 
                                 SetNewPasswordSchema, 
                                 MfaCodeSchema, 
                                 MfaVerifySchema)
from server.models import user
from utils.tokens import create_token, create_reset_token, decode_reset_token, create_mfa_token, decode_mfa_token
from utils.audit import log_action
from utils.decorators import login_required, current_user
from utils.validators import load_json

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/api/login")
def login():
    """
    Log in
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username: {type: string}
            password: {type: string}
    responses:
      200:
        description: Login successful, returns token
      401:
        description: Invalid credentials
    """
    data, err = load_json(LoginSchema)
    if err:
        return err

    user = User.query.filter_by(username=data["username"]).first()
    if not user or not user.check_password(data["password"]):
        return {"error": "Invalid username or password"}, 401
    if not user.is_active:
        return {"error": "Access denied. Contact IT."}, 403

    if user.mfa_enabled:
        return {"mfa_required": True, "mfa_token": create_mfa_token(user)}

    return {"token": create_token(user), "user": user.to_dict()}


@auth_bp.patch("/api/change_password")
@login_required
def change_password():
    """
    Change own password
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [old_password, new_password]
          properties:
            old_password: {type: string}
            new_password: {type: string}
    responses:
      200:
        description: Password changed
      400:
        description: Wrong current password or invalid input
    """
    data, err = load_json(ChangePasswordSchema)
    if err:
        return err

    if data["new_password"] != data["confirm_password"]:
        return {"error": "Passwords do not match"}, 400

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
    """
    Change own username
    ---
    tags:
      - Auth
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, password]
          properties:
            username: {type: string}
            password: {type: string}
    responses:
      200:
        description: Username changed
      400:
        description: Wrong password or invalid input
    """
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
    """
    Forgot password, step 2: verify recovery code
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [username, recovery_code]
          properties:
            username: {type: string}
            recovery_code: {type: string}
    responses:
      200:
        description: Code valid, returns reset token
      400:
        description: Invalid code
    """
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
    return {"reset_token": create_reset_token(user), "expires_in_seconds": 60}


@auth_bp.post("/api/set_new_password")
def set_new_password():
    """
    Forgot password, step 3: set a new password
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [reset_token, new_password, confirm_password]
          properties:
            reset_token: {type: string}
            new_password: {type: string}
            confirm_password: {type: string}
    responses:
      200:
        description: Password reset
      400:
        description: Invalid token or passwords do not match
    """
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

#-----MFA endpoints-----

@auth_bp.post("/api/mfa/verify")
def mfa_verify():
    """Login step 2: check the authenticator code, then issue the real token."""
    data, err = load_json(MfaVerifySchema)
    if err:
        return err

    try:
        payload = decode_mfa_token(data["mfa_token"])
        user = db.session.get(User, int(payload["sub"]))
    except jwt.ExpiredSignatureError:
        return {"error": "Session expired. Sign in again."}, 401
    except (jwt.InvalidTokenError, ValueError, TypeError):
        return {"error": "Invalid session. Sign in again."}, 401

    if (not user or not user.is_active or not user.mfa_enabled
            or payload.get("pwd") != user.password_hash[-12:]):
        return {"error": "Invalid session. Sign in again."}, 401

    if user.mfa_is_locked():
        return {"error": "Too many attempts. Try again in a few minutes."}, 429

    if not user.verify_mfa_code(data["code"]):
        db.session.commit()  # saves the failed-attempt count
        return {"error": "Invalid code. Access denied."}, 401

    db.session.commit()
    log_action("login_mfa", "user", user.id, actor_id=user.id)
    return {"token": create_token(user), "user": user.to_dict()}


@auth_bp.post("/api/mfa/setup")
@login_required
def mfa_setup():
    """Start MFA setup: returns the secret and the otpauth URI for the QR code."""
    user = current_user()
    if user.mfa_enabled:
        return {"error": "MFA is already enabled"}, 400
    uri = user.start_mfa_setup()
    db.session.commit()
    return {"secret": user.mfa_secret, "otpauth_uri": uri}


@auth_bp.post("/api/mfa/enable")
@login_required
def mfa_enable():
    """Finish setup: the user proves the app works by entering a valid code."""
    data, err = load_json(MfaCodeSchema)
    if err:
        return err

    user = current_user()
    if user.mfa_enabled or not user.mfa_secret:
        return {"error": "Start MFA setup first"}, 400
    if user.mfa_is_locked():
        return {"error": "Too many attempts. Try again in a few minutes."}, 429
    if not user.verify_mfa_code(data["code"]):
        db.session.commit()
        return {"error": "Invalid code"}, 400

    user.mfa_enabled = True
    log_action("mfa_enabled", "user", user.id)
    db.session.commit()
    return {"message": "MFA enabled", "user": user.to_dict()}