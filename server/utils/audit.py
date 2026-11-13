from extensions import db
from models.audit_log import AuditLog
from utils.decorators import current_user


def log_action(action, entity, entity_id=None, details=None, *, actor_id=None):
	"""Queue an audit record in the current transaction.

	``actor_id`` is useful for public flows such as password recovery, where
	the account whose password changed is the actor but is not logged in.
	The caller owns committing or rolling back the transaction.
	"""
	if actor_id is None:
		user = current_user()
		actor_id = user.id if user is not None else None
	if actor_id is None:
		raise RuntimeError("An authenticated actor is required to log this action")

	db.session.add(AuditLog(
		user_id=actor_id,
		action=action,
		entity=entity,
		entity_id=entity_id,
		details=details,
	))
