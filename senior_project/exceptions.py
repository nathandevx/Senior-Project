class CommandNotAllowedInProduction(Exception):
	"""When a custom django command like make_data.py or delete_data.py is run in production."""
	pass


class MoreThanOneActiveCartError(Exception):
	"""
	A person cannot have more than 1 active cart at a time.
	"""
	pass
