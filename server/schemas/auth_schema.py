import re
from marshmallow import Schema, fields, validate, pre_load, ValidationError, EXCLUDE
from models.user import ALL_ROLES

USERNAME_RE = re.compile(r"^[a-z0-9_.]{3,30}$")


#reusable fields 

class Username(fields.String):
    """Trims, lowercases, and checks the allowed characters."""
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs).strip().lower()
        if not USERNAME_RE.match(value):
            raise ValidationError("Must be 3-30 characters: letters, numbers, _ or .")
        return value


class Name(fields.String):
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs).strip()
        if not 1 <= len(value) <= 120:
            raise ValidationError("Must be 1-120 characters")
        return value


class Password(fields.String):
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        if len(value) < 8:
            raise ValidationError("Must be at least 8 characters")
        if len(value.encode("utf-8")) > 72:
            raise ValidationError("Must be at most 72 bytes (bcrypt limit)")
        return value


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE   # ignore fields we don't define

    @pre_load
    def blank_email_to_none(self, data, **kwargs):
        if isinstance(data, dict) and data.get("email") == "":
            data = {**data, "email": None}
        return data


def role_field(**kwargs):
    return fields.String(validate=validate.OneOf(sorted(ALL_ROLES)), **kwargs)


#input schemas: authentication (any employee) 

class LoginSchema(BaseSchema):
    username = Username(required=True)
    password = fields.String(required=True)


class ChangePasswordSchema(BaseSchema):
    old_password = fields.String(required=True)
    new_password = Password(required=True)


class ChangeUsernameSchema(BaseSchema):
    username = Username(required=True)
    password = fields.String(required=True)


class VerifyRecoveryCodeSchema(BaseSchema):
    username = Username(required=True)
    recovery_code = fields.String(required=True)


class SetNewPasswordSchema(BaseSchema):
    reset_token = fields.String(required=True)
    new_password = Password(required=True)
    confirm_password = fields.String(required=True)


#  input schemas: account management (IT only)

class RegisterEmployeeSchema(BaseSchema):
    name = Name(required=True)
    username = Username(required=True)
    role = role_field(required=True)
    email = fields.Email(allow_none=True)
    password = Password()          # optional: a temporary one is generated if missing


class ChangeDetailsSchema(BaseSchema):
    name = Name()
    username = Username()
    email = fields.Email(allow_none=True)
    role = role_field()


#  output schema

class UserSchema(Schema):
    """Output only. password_hash and recovery fields are never listed, so they can't leak."""
    id = fields.Int(dump_only=True)
    name = fields.String(dump_only=True)
    username = fields.String(dump_only=True)
    email = fields.String(dump_only=True, allow_none=True)
    role = fields.String(dump_only=True)
    is_active = fields.Boolean(dump_only=True)
    must_change_password = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)