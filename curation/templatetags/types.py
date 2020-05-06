from django import template

register = template.Library()


@register.filter
def types(name):
	if name is None:
		return 'mutant'
	if name == 'Wild type':
		return 'wildtype'
	elif ';' not in name:
		return 'Single mutant'
	elif name.count(';') == 1:
		return 'Double mutant'
	elif name.count(';') == 2:
		return 'Triple mutant'
	elif name.count(';') == 3:
		return '4-mutant'
	elif name.count(';') == 4:
		return '5-mutant'
	elif name.count(';') == 5:
		return '6-mutant'
	else:
		return 'mutant'
