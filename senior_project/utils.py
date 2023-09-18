from django.utils import timezone


def format_datetime(datetime_obj):
	"""
	Formats a datetime object.
	Ex: "September 12, 2023, at 08:19 AM"
	@param datetime_obj: datetime object.
	@return: a formatted datetime object.
	"""
	return timezone.localtime(datetime_obj).strftime('%B %d, %Y, %I:%M %p')
