from datetime import datetime, timedelta, timezone
import jwt
from extensions import db
from models.audit_log import AuditLog
from utils.tokens import create_reset_token


def login(client, username, password):
    return client.post("/api/login", json={"username": username, "password": password})


def issue_code(get_user, uid):
    """What IT's POST /api/recovery_code/<id> does."""
    user = get_user(uid)
    code = user.generate_recovery_code()
    db.session.commit()
    return code


# ---------------- login ----------------

def test_login_success(client, make_user):
    make_user("sam")
    res = login(client, "sam", "Password123")
    assert res.status_code == 200
    body = res.get_json()
    assert body["token"]
    assert body["user"]["username"] == "sam"
    assert "password_hash" not in body["user"]


def test_login_wrong_password(client, make_user):
    make_user("sam")
    res = login(client, "sam", "WrongPass999")
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid username or password"


def test_login_unknown_user_gives_same_error(client):
    res = login(client, "ghost", "Password123")
    assert res.status_code == 401
    assert res.get_json()["error"] == "Invalid username or password"


def test_login_disabled_account(client, make_user):
    make_user("sam", is_active=False)
    res = login(client, "sam", "Password123")
    assert res.status_code == 403


def test_login_missing_fields(client):
    res = client.post("/api/login", json={"username": "sam"})
    assert res.status_code == 400


def test_login_no_body(client):
    res = client.post("/api/login")
    assert res.status_code == 400


# ---------------- change_password ----------------

def test_change_password_success(client, make_user, auth_header, get_user):
    uid = make_user("sam", must_change_password=True)
    res = client.patch("/api/change_password", headers=auth_header(uid),
                       json={"old_password": "Password123", "new_password": "NewPass456"})
    assert res.status_code == 200
    assert get_user(uid).must_change_password is False
    assert login(client, "sam", "NewPass456").status_code == 200
    assert login(client, "sam", "Password123").status_code == 401
    assert AuditLog.query.filter_by(action="change_password", user_id=uid).count() == 1


def test_change_password_requires_login(client):
    res = client.patch("/api/change_password",
                       json={"old_password": "a", "new_password": "NewPass456"})
    assert res.status_code == 401


def test_change_password_wrong_old(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_password", headers=auth_header(uid),
                       json={"old_password": "Nope12345", "new_password": "NewPass456"})
    assert res.status_code == 400


def test_change_password_same_as_old(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_password", headers=auth_header(uid),
                       json={"old_password": "Password123", "new_password": "Password123"})
    assert res.status_code == 400


def test_change_password_too_short(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_password", headers=auth_header(uid),
                       json={"old_password": "Password123", "new_password": "short"})
    assert res.status_code == 400


def test_change_password_too_long_for_bcrypt(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_password", headers=auth_header(uid),
                       json={"old_password": "Password123", "new_password": "x" * 73})
    assert res.status_code == 400


def test_disabled_user_token_stops_working(client, make_user, auth_header, get_user):
    uid = make_user("sam")
    headers = auth_header(uid)
    user = get_user(uid)
    user.is_active = False
    db.session.commit()
    res = client.patch("/api/change_password", headers=headers,
                       json={"old_password": "Password123", "new_password": "NewPass456"})
    assert res.status_code == 401


# ---------------- change_username ----------------

def test_change_username_success(client, make_user, auth_header, get_user):
    uid = make_user("sam")
    res = client.patch("/api/change_username", headers=auth_header(uid),
                       json={"username": "Samuel.K", "password": "Password123"})
    assert res.status_code == 200
    assert get_user(uid).username == "samuel.k"       # lowercased
    assert login(client, "samuel.k", "Password123").status_code == 200


def test_change_username_wrong_password(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_username", headers=auth_header(uid),
                       json={"username": "newname", "password": "WrongPass999"})
    assert res.status_code == 400


def test_change_username_taken(client, make_user, auth_header):
    uid = make_user("sam")
    make_user("jane")
    res = client.patch("/api/change_username", headers=auth_header(uid),
                       json={"username": "jane", "password": "Password123"})
    assert res.status_code == 409


def test_change_username_invalid_format(client, make_user, auth_header):
    uid = make_user("sam")
    res = client.patch("/api/change_username", headers=auth_header(uid),
                       json={"username": "bad name!", "password": "Password123"})
    assert res.status_code == 400


def test_change_username_requires_login(client):
    res = client.patch("/api/change_username",
                       json={"username": "newname", "password": "Password123"})
    assert res.status_code == 401


# ---------------- verify_recovery_code ----------------

def test_verify_code_success_returns_reset_token(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": code})
    assert res.status_code == 200
    assert res.get_json()["reset_token"]
    assert get_user(uid).recovery_code_hash is None     # code burned after use


def test_verify_code_is_single_use(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    body = {"username": "sam", "recovery_code": code}
    assert client.post("/api/verify_recovery_code", json=body).status_code == 200
    assert client.post("/api/verify_recovery_code", json=body).status_code == 400


def test_verify_code_wrong_code(client, make_user, get_user):
    uid = make_user("sam")
    issue_code(get_user, uid)
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": "AAAA-BBBB-CCCC"})
    assert res.status_code == 400
    assert get_user(uid).recovery_attempts == 1


def test_verify_code_is_case_insensitive(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": code.lower()})
    assert res.status_code == 200


def test_verify_code_expired(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    user = get_user(uid)
    user.recovery_code_expires = datetime.utcnow() - timedelta(minutes=1)
    db.session.commit()
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": code})
    assert res.status_code == 400


def test_verify_code_locks_after_five_wrong_attempts(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    for _ in range(5):
        client.post("/api/verify_recovery_code",
                    json={"username": "sam", "recovery_code": "AAAA-BBBB-CCCC"})
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": code})   # correct, but locked
    assert res.status_code == 400


def test_verify_code_no_code_issued(client, make_user):
    make_user("sam")
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": "AAAA-BBBB-CCCC"})
    assert res.status_code == 400


def test_verify_code_disabled_user(client, make_user, get_user):
    uid = make_user("sam")
    code = issue_code(get_user, uid)
    user = get_user(uid)
    user.is_active = False
    db.session.commit()
    res = client.post("/api/verify_recovery_code",
                      json={"username": "sam", "recovery_code": code})
    assert res.status_code == 400


def test_verify_code_unknown_user_same_error(client):
    res = client.post("/api/verify_recovery_code",
                      json={"username": "ghost", "recovery_code": "AAAA-BBBB-CCCC"})
    assert res.status_code == 400
    assert res.get_json()["error"] == "Invalid or expired recovery code"


# ---------------- set_new_password ----------------

def reset_token_for(client, get_user, uid, username="sam"):
    code = issue_code(get_user, uid)
    res = client.post("/api/verify_recovery_code",
                      json={"username": username, "recovery_code": code})
    return res.get_json()["reset_token"]


def test_full_forgot_password_flow(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    res = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert res.status_code == 200
    assert login(client, "sam", "BrandNew789").status_code == 200
    assert login(client, "sam", "Password123").status_code == 401
    log = AuditLog.query.filter_by(action="recover_password", user_id=uid).first()
    assert log is not None


def test_set_new_password_clears_must_change_flag(client, make_user, get_user):
    uid = make_user("sam", must_change_password=True)
    token = reset_token_for(client, get_user, uid)
    client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert get_user(uid).must_change_password is False


def test_set_new_password_mismatch(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    res = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "BrandNew789",
        "confirm_password": "Different000"})
    assert res.status_code == 400
    assert login(client, "sam", "Password123").status_code == 200   # unchanged


def test_set_new_password_too_short(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    res = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "short", "confirm_password": "short"})
    assert res.status_code == 400


def test_set_new_password_garbage_token(client):
    res = client.post("/api/set_new_password", json={
        "reset_token": "not-a-token", "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert res.status_code == 400


def test_login_token_cannot_be_used_as_reset_token(client, make_user, auth_header):
    uid = make_user("sam")
    login_token = auth_header(uid)["Authorization"].split(" ")[1]
    res = client.post("/api/set_new_password", json={
        "reset_token": login_token, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert res.status_code == 400


def test_reset_token_cannot_be_used_to_log_in(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    res = client.patch("/api/change_password",
                       headers={"Authorization": f"Bearer {token}"},
                       json={"old_password": "Password123", "new_password": "NewPass456"})
    assert res.status_code == 401


def test_reset_token_is_single_use(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    first = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    second = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "Another1234",
        "confirm_password": "Another1234"})
    assert first.status_code == 200
    assert second.status_code == 400
    assert login(client, "sam", "BrandNew789").status_code == 200


def test_set_new_password_expired_token(client, app, make_user, get_user):
    uid = make_user("sam")
    user = get_user(uid)
    now = datetime.now(timezone.utc)
    expired = jwt.encode(
        {"sub": str(uid), "purpose": "password_reset",
         "pwd": user.password_hash[-12:],
         "iat": now - timedelta(minutes=20), "exp": now - timedelta(minutes=10)},
        app.config["JWT_SECRET_KEY"] + "-password-reset", algorithm="HS256")
    res = client.post("/api/set_new_password", json={
        "reset_token": expired, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert res.status_code == 400
    assert "expired" in res.get_json()["error"].lower()


def test_set_new_password_disabled_user(client, make_user, get_user):
    uid = make_user("sam")
    token = reset_token_for(client, get_user, uid)
    user = get_user(uid)
    user.is_active = False
    db.session.commit()
    res = client.post("/api/set_new_password", json={
        "reset_token": token, "new_password": "BrandNew789",
        "confirm_password": "BrandNew789"})
    assert res.status_code == 400