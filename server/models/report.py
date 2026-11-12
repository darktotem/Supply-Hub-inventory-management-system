from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request

from app.extensions import db
from app.models.report import Report

reports_bp = Blueprint("reports", __name__, url_prefix="/api")

READERS = ("store_worker", "operations_director", "auditor")


def _error(message, status):
    return jsonify({"error": message}), status


def role_required(*roles):
    """Needs a Bearer JWT (HS256, SECRET_KEY) with a `role` claim in `roles`."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return _error("Authentication required", 401)
            try:
                claims = jwt.decode(header[7:], current_app.config["SECRET_KEY"],
                                    algorithms=["HS256"])
            except jwt.PyJWTError:
                return _error("Invalid or expired token", 401)
            if claims.get("role") not in roles:
                return _error("You do not have permission to do this", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@reports_bp.get("/reports")
@role_required(*READERS)
def list_reports():
    query = Report.query.order_by(Report.created_on.desc(), Report.id.desc())
    search = request.args.get("search", "").strip()
    if search:
        query = query.filter(Report.name.ilike(f"%{search}%"))
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    except ValueError:
        return _error("'page' and 'per_page' must be integers", 400)
    p = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "reports": [r.to_dict() for r in p.items],
        "page": p.page, "per_page": p.per_page,
        "total": p.total, "pages": p.pages,
    })


@reports_bp.get("/reports/<int:report_id>")
@role_required(*READERS)
def get_report(report_id):
    report = db.session.get(Report, report_id)
    if report is None:
        return _error("Report not found", 404)
    return jsonify(report.to_dict())


@reports_bp.post("/reports")
@role_required("store_worker")
def create_report():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return _error("Request body must be a JSON object", 400)
    name, body = data.get("name"), data.get("report")
    if not isinstance(name, str) or not name.strip():
        return _error("'name' is required", 400)
    if not isinstance(body, str) or not body.strip():
        return _error("'report' is required", 400)
    name, body = name.strip(), body.strip()
    if len(name) > 120:
        return _error("'name' must be at most 120 characters", 400)
    if len(body) > 20000:
        return _error("'report' must be at most 20000 characters", 400)
    report = Report(name=name, report=body)
    db.session.add(report)
    db.session.commit()
    return jsonify(report.to_dict()), 201


@reports_bp.delete("/reports/<int:report_id>")
@role_required("operations_director")
def delete_report(report_id):
    report = db.session.get(Report, report_id)
    if report is None:
        return _error("Report not found", 404)
    db.session.delete(report)
    db.session.commit()
    return jsonify({"message": "Report deleted"}), 200