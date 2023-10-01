class CommandNotAllowedInProduction(Exception):
	"""When a custom django command like make_data.py or delete_data.py is run in production."""
	pass


class MoreThanOneActiveCartError(Exception):
	"""
	A person cannot have more than 1 active cart at a time.
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
