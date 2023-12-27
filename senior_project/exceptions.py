class CommandNotAllowedInProduction(Exception):
	"""When a custom django command like make_random_data.py or delete_data.py is run in production."""
	pass


class MoreThanOneActiveCartError(Exception):
	"""
	A person cannot have more than 1 active cart at a time.
	"""
	pass


class MoreThanOneCartItemError(Exception):
	"""
	A person can have only 1 cart. That cart can only have 1 cart item per product. There was probably an error with
	deleting a cart item after the cart was deleted.
	"""
	pass


class ErrorCreatingAStripeProduct(Exception):
	"""
	When an error occurs when creating a product on stripe.
	The created product is deleted from the website if this happens.
	"""
	pass


class ErrorUpdatingAStripeProduct(Exception):
	"""
	When an error occurs when updating a product on stripe.
	The updated product is not saved to the website if this happens.
	"""
	pass


class ErrorDeletingAStripeProduct(Exception):
	"""
	When an error occurs when updating a product on stripe.
	The updated product is not saved to the website if this happens.
	"""
	pass


class ErrorCreatingStripeCheckoutSession(Exception):
	"""
	When an error occurs when creating a stripe checkout session.
	"""
	pass


class MultipleOrdersForCart(Exception):
	"""A cart has multiple orders associated to it. It should only have 1 order at most associated with it."""
	pass
