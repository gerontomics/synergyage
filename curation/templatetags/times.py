from django import template

register = template.Library()


@register.filter
def times(val):
	return round(1 + (val / 100), 2)
