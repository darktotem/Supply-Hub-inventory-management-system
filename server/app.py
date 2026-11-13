from flask import Flask, request
from config import Config
from extensions import db, migrate, bcrypt
from models import Inventory, Invoice, Supplier, SupplyHistory, AuditLog, Customer, CustomerHistory, User

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



from controllers.auth import auth_bp  
from controllers.supply import supply_bp  
from controllers.invoice import invoice_bp
from controllers.sales import sales_bp
from controllers.warehouse import warehouse_bp


app.register_blueprint(auth_bp)
app.register_blueprint(supply_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(warehouse_bp)

if __name__ == "__main__":
    app.run(debug=True)