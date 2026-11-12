from flask import Flask

from app.extensions import db
from app.models.report import Report  # noqa: F401  (registers the table)
from app.api.reports import reports_bp

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev_reports.db"
app.config["SECRET_KEY"] = "change-me"

db.init_app(app)
app.register_blueprint(reports_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
    