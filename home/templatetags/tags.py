from django import template
from home.models import Cart, Configurations

register = template.Library()


@register.simple_tag(takes_context=True)
def cart_url(context):
	cart = Cart.get_active_cart_or_create_new_cart(context['request'])
	return cart.get_read_url()


@register.simple_tag
def config_url():
	if Configurations.config_exists():
		url = Configurations.get_first_configuration().get_read_url()
	else:
		url = Configurations.get_create_url()
	return url
