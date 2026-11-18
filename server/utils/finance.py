import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from extensions import db
from models.audit import AuditLog

GENESIS_HASH = "0" * 64
TWO_PLACES = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def refresh_status(invoice) -> None:
    if invoice.status == "void":
        return

    paid = money(invoice.amount_paid or 0)
    total = money(invoice.total)

    if paid <= 0:
        invoice.status = "pending"
    elif paid < total:
        invoice.status = "partial"
    else:
        invoice.status = "paid"


def _digest(prev_hash: str, entry: AuditLog) -> str:
    body = json.dumps(
        {
            "entity": entry.entity,
            "entity_id": entry.entity_id,
            "action": entry.action,
            "old": entry.old_values,
            "new": entry.new_values,
            "user_id": entry.user_id,
            "at": entry.created_at,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256((prev_hash + body).encode()).hexdigest()


def log_audit(entity, entity_id, action, old=None, new=None, user_id=None) -> AuditLog:
    last = (
        db.session.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .with_for_update()         
        .first()
    )
    prev_hash = last.hash if last else GENESIS_HASH

    entry = AuditLog(
        entity=entity,
        entity_id=entity_id,
        action=action,
        old_values=old,
        new_values=new,
        user_id=user_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        prev_hash=prev_hash,
        hash="",                  
    )
    entry.hash = _digest(prev_hash, entry)
    db.session.add(entry)
    return entry


def verify_audit_chain():
    prev_hash = GENESIS_HASH
    for entry in AuditLog.query.order_by(AuditLog.id):
        if entry.prev_hash != prev_hash or entry.hash != _digest(prev_hash, entry):
            return False, entry.id
        prev_hash = entry.hash
    return True, None