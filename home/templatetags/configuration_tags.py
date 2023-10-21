from django import template
from home.models import Configurations

register = template.Library()


@register.simple_tag
def config_url():
	if Configurations.config_exists():
		url = Configurations.get_first_configuration().get_read_url()
	else:
		url = Configurations.get_create_url()
	return url
