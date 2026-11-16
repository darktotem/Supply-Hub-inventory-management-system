from sqlalchemy import update

from extensions import db
from models.inventory import Inventory

def _validate_quantity(quantity):
	if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
		raise ValueError("quantity must be a positive integer")

def take_stock(product_id, quantity):
    """Subtract stock in ONE database step, so it is safe when requests arrive together.

    Returns True if the stock was taken, or False if there was not enough.
    It does not commit. The caller commits (or rolls back).
    """
    _validate_quantity(quantity)
    result = db.session.execute(
        update(Inventory)
        .where(Inventory.id == product_id, Inventory.quantity >= quantity)
        .values(quantity=Inventory.quantity - quantity)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount == 1


def add_stock(product_id, quantity):
    """Add stock in ONE database step, so it is safe when requests arrive together.

    Returns True if the stock was added, or False if the product does not exist.
    It does not commit. The caller commits (or rolls back).
    """
    _validate_quantity(quantity)
    result = db.session.execute(
        update(Inventory)
        .where(Inventory.id == product_id)
        .values(quantity=Inventory.quantity + quantity)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount == 1


def increase_stock(item, quantity):
	"""Increase an inventory-like model's quantity and return the new value."""
	_validate_quantity(quantity)
	if not hasattr(item, "quantity"):
		raise TypeError("item must have a quantity attribute")

	item.quantity += quantity
	return item.quantity


def decrease_stock(item, quantity):
	"""Decrease stock, refusing invalid quantities or insufficient stock."""
	_validate_quantity(quantity)
	if not hasattr(item, "quantity"):
		raise TypeError("item must have a quantity attribute")
	if item.quantity < quantity:
		raise ValueError("insufficient stock")

	item.quantity -= quantity
	return item.quantity