def _validate_quantity(quantity):
	if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
		raise ValueError("quantity must be a positive integer")


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
