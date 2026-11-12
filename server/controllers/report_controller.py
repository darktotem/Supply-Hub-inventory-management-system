from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from extensions import db
from models.report import Report
from schemas.report_schema import (
    create_report_schema,
    list_reports_query_schema,
    report_id_schema,
)
from utils.decorators import login_required, current_user

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

READERS = ("store_worker", "operations_director", "auditor")


def _validation_error(err):
    """One clean 400 response for any schema failure."""
    return jsonify({"error": "Invalid input", "details": err.messages}), 400


def _not_allowed(*roles):
    """Returns a 403 response if the logged-in user's role is not in `roles`."""
    user = current_user()
    if user is None or user.role not in roles:
        return jsonify({"error": "You do not have permission to do this"}), 403
    return None


# 1. CREATE ----------------------------------------------------------------
@reports_bp.post("")
@login_required
def create_report():
    denied = _not_allowed("store_worker")
    if denied:
        return denied

    try:
        data = create_report_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return _validation_error(err)

    report = Report(name=data["name"], report=data["report"])
    db.session.add(report)
    db.session.commit()
    return jsonify(report.to_dict()), 201


# 2. LIST ------------------------------------------------------------------
@reports_bp.get("")
@login_required
def list_reports():
    denied = _not_allowed(*READERS)
    if denied:
        return denied

    try:
        args = list_reports_query_schema.load(request.args)
    except ValidationError as err:
        return _validation_error(err)

    query = Report.query.order_by(Report.created_on.desc(), Report.id.desc())
    if args["search"]:
        query = query.filter(Report.name.ilike(f"%{args['search']}%"))

    page = query.paginate(page=args["page"], per_page=args["per_page"],
                          error_out=False)
    return jsonify({
        "reports": [r.to_dict() for r in page.items],
        "page": page.page,
        "per_page": page.per_page,
        "total": page.total,
        "pages": page.pages,
    })


# 3. VIEW ONE --------------------------------------------------------------
@reports_bp.get("/<int:report_id>")
@login_required
def get_report(report_id):
    denied = _not_allowed(*READERS)
    if denied:
        return denied

    try:
        report_id = report_id_schema.load({"report_id": report_id})["report_id"]
    except ValidationError as err:
        return _validation_error(err)

    report = db.session.get(Report, report_id)
    if report is None:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report.to_dict())


# 4. DELETE ----------------------------------------------------------------
@reports_bp.delete("/<int:report_id>")
@login_required
def delete_report(report_id):
    denied = _not_allowed("operations_director")
    if denied:
        return denied

    try:
        report_id = report_id_schema.load({"report_id": report_id})["report_id"]
    except ValidationError as err:
        return _validation_error(err)

    report = db.session.get(Report, report_id)
    if report is None:
        return jsonify({"error": "Report not found"}), 404
    db.session.delete(report)
    db.session.commit()
    return jsonify({"message": "Report deleted"}), 200