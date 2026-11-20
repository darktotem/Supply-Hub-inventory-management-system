from flask import Flask, request, jsonify
from config import Config
from extensions import db, migrate, bcrypt
from flasgger import Swagger

# Import Models
from models import Inventory, Invoice, Supplier, SupplyHistory, AuditLog, Customer, CustomerHistory, User, Payment

# Import decorators
from controllers.auth import auth_bp  
from controllers.supply import supply_bp  
from controllers.invoice import invoice_bp
from controllers.sales import sales_bp
from controllers.warehouse import warehouse_bp
from controllers.inventory import inventory_bp
from controllers.audit import audit_bp
from controllers.employees import employees_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
swagger = Swagger(app)

@app.route
def colors(palette):
    """
    Get a list of colors based on the chosen palette.
    ---
    parameters:
      - name: palette
        in: path
        type: string
        required: true
        description: The name of the palette (e.g., pastel, neon)
    responses:
      200:
        description: A list of colors
    """
    if palette == 'pastel':
        return jsonify(['lavender', 'mint', 'peach'])
    return jsonify(['black', 'white'])


@app.after_request
def add_cors_headers(response):
    """Lets the Vite app (port 5173) call this API. Replaces flask-cors."""
    origin = request.headers.get("Origin")
    if origin and origin in app.config["CORS_ORIGINS"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST,PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Max-Age"] = "600"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# Register decorators
app.register_blueprint(inventory_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(supply_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(warehouse_bp)
app.register_blueprint(audit_bp)
app.register_blueprint(employees_bp)



if __name__ == "__main__":
    app.run(debug=True)