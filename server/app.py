from flask import Flask, request
from config import Config
from extensions import db, migrate, bcrypt

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)


@app.after_request
def add_cors_headers(response):
    """Lets the Vite app (port 5173) call this API. Replaces flask-cors."""
    origin = request.headers.get("Origin")
    if origin and origin in app.config["CORS_ORIGINS"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST,PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Max-Age"] = "600"
        response.headers["Vary"] = "Origin"
    return response


import models  # noqa: E402,F401  (so migrations see all models)


# from utils.errors import register_error_handlers  # noqa: E402
# register_error_handlers(app)

# Controller files go LAST. Each one does `from app import app`.
import controllers.inventory   # noqa: E402,F401

if __name__ == "__main__":
    app.run(debug=True)


#report controller blue print

from controllers.report_controller import reports_bp
app.register_blueprint(reports_bp)