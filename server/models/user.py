import secrets
from datetime import datetime, timedelta
from extensions import db, bcrypt


class Role:
    OPERATIONS_DIRECTOR = "operations_director"
    IT_ADMIN = "it_admin"
    PROCUREMENT = "procurement_officer"
    STORE_WORKER = "store_worker"
    SALES = "sales_officer"
    FINANCE = "finance_officer"
    AUDITOR = "auditor"


ALL_ROLES = {
    Role.OPERATIONS_DIRECTOR, Role.IT_ADMIN, Role.PROCUREMENT,
    Role.STORE_WORKER, Role.SALES, Role.FINANCE, Role.AUDITOR,
}

MAX_RECOVERY_ATTEMPTS = 5


def _matches(hashed, raw):
    try:
        return bcrypt.check_password_hash(hashed, raw)
    except ValueError:  # e.g. input longer than bcrypt's 72-byte limit
        return False


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)

    recovery_code_hash = db.Column(db.String(256))
    recovery_code_expires = db.Column(db.DateTime)
    recovery_attempts = db.Column(db.Integer, default=0, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = bcrypt.generate_password_hash(raw).decode("utf-8")

    def check_password(self, raw):
        return _matches(self.password_hash, raw)

    def generate_recovery_code(self, hours=24):
        """Returns the plain code (shown once). Only the hash is stored."""
        code = "-".join(secrets.token_hex(2).upper() for _ in range(3))  # A1B2-C3D4-E5F6
        self.recovery_code_hash = bcrypt.generate_password_hash(code).decode("utf-8")
        self.recovery_code_expires = datetime.utcnow() + timedelta(hours=hours)
        self.recovery_attempts = 0
        return code

    def clear_recovery_code(self):
        self.recovery_code_hash = None
        self.recovery_code_expires = None
        self.recovery_attempts = 0

    def verify_recovery_code(self, code):
        if not self.recovery_code_hash or not self.recovery_code_expires:
            return False
        if self.recovery_code_expires < datetime.utcnow():
            return False
        if self.recovery_attempts >= MAX_RECOVERY_ATTEMPTS:
            return False
        if _matches(self.recovery_code_hash, (code or "").strip().upper()):
            return True
        self.recovery_attempts += 1
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "must_change_password": self.must_change_password,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }