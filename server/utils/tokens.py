from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


def _secret_key():
	return current_app.config.get("JWT_SECRET_KEY") or current_app.secret_key


def _encode(payload):
	return jwt.encode(payload, _secret_key(), algorithm="HS256")


def _decode(token, expected_type):
	payload = jwt.decode(
		token,
		_secret_key(),
		algorithms=["HS256"],
		options={"require": ["exp", "iat", "sub", "typ"]},
	)
	if payload.get("typ") != expected_type:
		raise jwt.InvalidTokenError("Unexpected token type")
	return payload


def create_token(user):
	"""Create a signed access token, invalidated when the password changes."""
	now = datetime.now(timezone.utc)
	lifetime_hours = current_app.config.get("JWT_EXPIRES_HOURS", 8)
	payload = {
		"sub": str(user.id),
		"typ": "access",
		"pwd": user.password_hash[-12:],
		"iat": now,
		"exp": now + timedelta(hours=lifetime_hours),
	}
	return _encode(payload)


def decode_token(token):
	"""Decode and validate an access token."""
	return _decode(token, "access")


def create_reset_token(user):
	"""Create a short-lived reset token tied to the current password hash."""
	now = datetime.now(timezone.utc)
	payload = {
		"sub": str(user.id),
		"typ": "password_reset",
		"pwd": user.password_hash[-12:],
		"iat": now,
		"exp": now + timedelta(minutes=10),
	}
	return _encode(payload)


def decode_reset_token(token):
	"""Decode a password-reset token; rejects access tokens and other JWTs."""
	return _decode(token, "password_reset")
