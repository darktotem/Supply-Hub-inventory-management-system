from flask import request
from marshmallow import ValidationError


def load_json(schema_type):
	"""Validate a JSON object with a Marshmallow schema.

	The return shape is ``(data, error_response)`` to match the auth routes.
	"""
	payload = request.get_json(silent=True)
	if not isinstance(payload, dict):
		return None, ({"error": "Request body must be a JSON object"}, 400)

	try:
		data = schema_type().load(payload)
	except ValidationError as error:
		return None, ({"errors": error.messages}, 400)

	return data, None
