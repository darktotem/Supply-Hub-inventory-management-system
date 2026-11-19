from flask import Blueprint, jsonify

from utils.finance import verify_audit_chain
from extensions import db

audit_bp = Blueprint("audit", __name__, url_prefix="/audits")

@audit_bp.route("/verify", methods=["GET"])
def verify_audit():
    """
    Verify the audit log chain
    ---
    tags:
      - Audit
    responses:
      200:
        description: Chain validity result
    """
    valid, broken_at = verify_audit_chain()
    return jsonify({"valid": valid, "broken_at": broken_at}), 200