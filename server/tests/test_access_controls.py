from datetime import datetime, timedelta, timezone

import jwt
import pytest
from flask import Flask

from extensions import db, bcrypt
from models.user import User, Role
from utils.decorators import login_required, roles_required
from utils.tokens import create_token

SECRET = "test-secret"
MUTATIONS = ["POST", "PUT", "PATCH", "DELETE"]


@pytest.fixture()
def access_app():
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY=SECRET,
        JWT_SECRET_KEY=SECRET,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )
    db.init_app(app)
    bcrypt.init_app(app)

    @app.route("/any-user", methods=MUTATIONS)
    @login_required
    def any_user():
        return {"ok": True}, 200

    @app.route("/procurement-only", methods=MUTATIONS)
    @roles_required(Role.PROCUREMENT, Role.OPERATIONS_DIRECTOR)
    def procurement_only():
        return {"ok": True}, 200

    with app.app_context():
        db.create_all()
        for username, role in [
            ("proc", Role.PROCUREMENT),
            ("director", Role.OPERATIONS_DIRECTOR),
            ("worker", Role.STORE_WORKER),
            ("auditor", Role.AUDITOR),
        ]:
            user = User(name=username, username=username,
                        email=f"{username}@test.com", role=role)
            user.set_password("Password123!")
            db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(access_app):
    return access_app.test_client()


def _token_for(app, username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        return create_token(user)


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Anonymous users ----------

@pytest.mark.parametrize("method", MUTATIONS)
@pytest.mark.parametrize("path", ["/any-user", "/procurement-only"])
def test_anonymous_gets_401(client, method, path):
    response = client.open(path, method=method)
    assert response.status_code == 401


def test_malformed_auth_header_gets_401(client):
    for header in ["Token abc", "Bearer", "Bearer ", "abc"]:
        response = client.post("/any-user", headers={"Authorization": header})
        assert response.status_code == 401


def test_garbage_token_gets_401(client):
    response = client.post("/any-user", headers=_auth("not.a.jwt"))
    assert response.status_code == 401


def test_expired_token_gets_401(client, access_app):
    with access_app.app_context():
        user = User.query.filter_by(username="proc").first()
        now = datetime.now(timezone.utc)
        expired = jwt.encode(
            {
                "sub": str(user.id),
                "typ": "access",
                "pwd": user.password_hash[-12:],
                "iat": now - timedelta(hours=10),
                "exp": now - timedelta(hours=2),
            },
            SECRET,
            algorithm="HS256",
        )
    response = client.post("/procurement-only", headers=_auth(expired))
    assert response.status_code == 401


def test_reset_token_cannot_be_used_as_access_token(client, access_app):
    from utils.tokens import create_reset_token
    with access_app.app_context():
        user = User.query.filter_by(username="proc").first()
        reset = create_reset_token(user)
    response = client.post("/any-user", headers=_auth(reset))
    assert response.status_code == 401


# ---------- Unauthorized roles ----------

@pytest.mark.parametrize("method", MUTATIONS)
@pytest.mark.parametrize("username", ["worker", "auditor"])
def test_wrong_role_gets_403(client, access_app, method, username):
    token = _token_for(access_app, username)
    response = client.open("/procurement-only", method=method, headers=_auth(token))
    assert response.status_code == 403


# ---------- Allowed roles (proves decorators don't block everyone) ----------

@pytest.mark.parametrize("method", MUTATIONS)
@pytest.mark.parametrize("username", ["proc", "director"])
def test_allowed_role_gets_200(client, access_app, method, username):
    token = _token_for(access_app, username)
    response = client.open("/procurement-only", method=method, headers=_auth(token))
    assert response.status_code == 200


def test_any_logged_in_role_passes_login_required(client, access_app):
    token = _token_for(access_app, "auditor")
    response = client.post("/any-user", headers=_auth(token))
    assert response.status_code == 200


# ---------- Token invalidation ----------

def test_deactivated_user_gets_401(client, access_app):
    token = _token_for(access_app, "proc")
    with access_app.app_context():
        user = User.query.filter_by(username="proc").first()
        user.is_active = False
        db.session.commit()
    response = client.post("/procurement-only", headers=_auth(token))
    assert response.status_code == 401


def test_old_token_rejected_after_password_change(client, access_app):
    token = _token_for(access_app, "proc")
    with access_app.app_context():
        user = User.query.filter_by(username="proc").first()
        user.set_password("NewPassword456!")
        db.session.commit()
    response = client.post("/procurement-only", headers=_auth(token))
    assert response.status_code == 401