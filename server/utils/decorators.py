from functools import wraps

import jwt
from flask import g, request

from extensions import db
from models.user import User
from utils.tokens import decode_token


def current_user():
	"""Return the authenticated user for the current request, if any."""
	return getattr(g, "authenticated_user", None)


def login_required(view):
	"""Require a valid Bearer access token before invoking a route."""
	@wraps(view)
	def wrapped(*args, **kwargs):
		authorization = request.headers.get("Authorization", "")
		scheme, separator, token = authorization.partition(" ")
		if scheme.lower() != "bearer" or not separator or not token.strip():
			return {"error": "Authentication required"}, 401

		try:
			payload = decode_token(token.strip())
			user_id = int(payload["sub"])
			user = db.session.get(User, user_id)
		except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
			return {"error": "Authentication required"}, 401

		if (user is None or not user.is_active
				or payload.get("pwd") != user.password_hash[-12:]):
			return {"error": "Authentication required"}, 401

		g.authenticated_user = user
		return view(*args, **kwargs)

	return wrapped


def roles_required(*allowed_roles):
	"""Require authentication and one of the specified user roles."""
	if not allowed_roles or any(not isinstance(role, str) for role in allowed_roles):
		raise ValueError("roles_required expects one or more role names")

	def decorator(view):
		@wraps(view)
		@login_required
		def wrapped(*args, **kwargs):
			user = current_user()
			if user is None or user.role not in allowed_roles:
				return {"error": "You do not have permission to access this resource"}, 403
			return view(*args, **kwargs)

		return wrapped

	return decorator
