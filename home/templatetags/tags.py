from django import template
from home.models import Cart

register = template.Library()


@register.simple_tag(takes_context=True)
def cart_url(context):
	cart = Cart.get_active_cart_or_create_new_cart(context['request'].user)
	return cart.get_read_url()
