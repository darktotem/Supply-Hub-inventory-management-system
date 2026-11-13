from flask import Flask
from werkzeug.exceptions import HTTPException


def register_error_handlers(app: Flask):
	"""Register consistent JSON responses for common Flask errors."""
	@app.errorhandler(HTTPException)
	def handle_http_error(error):
		return {"error": error.description}, error.code

	@app.errorhandler(Exception)
	def handle_unexpected_error(error):
		app.logger.exception("Unhandled application error", exc_info=error)
		return {"error": "An unexpected error occurred"}, 500
