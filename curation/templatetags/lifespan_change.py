from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def lifespan_change(name, model_min_lifespan, model_max_lifespan, organism_min_lifespan, organism_max_lifespan):
	if model_min_lifespan == model_max_lifespan:
		min = (model_min_lifespan - organism_max_lifespan) * 100 / organism_max_lifespan
		max = (model_min_lifespan - organism_min_lifespan) * 100 / organism_min_lifespan
	else:
		min = (model_min_lifespan - organism_max_lifespan) * 100 / organism_max_lifespan
		max = (model_min_lifespan - organism_max_lifespan) * 100 / organism_min_lifespan

	# min_times = round(1 + (min / 100), 2)
	# max_times = round(1 + (max / 100), 2)

	min = round(min, 2)
	max = round(max, 2)
	organism_min_lifespan = round(organism_min_lifespan, 2)
	organism_max_lifespan = round(organism_max_lifespan, 2)

	min_html = '<small class="text-muted">'
	max_html = '<small class="text-muted">'

	if min > 0:
		min_html += '<i class="fa fa-arrow-circle-up" aria-hidden="true"></i>'
	elif min == 0:
		min_html += '<i class="fa fa-circle" aria-hidden="true"></i>'
	else:
		min_html += '<i class="fa fa-arrow-circle-down" aria-hidden="true"></i>'

	if max > 0:
		max_html += '<i class="fa fa-arrow-circle-up" aria-hidden="true"></i>'
	elif max == 0:
		max_html += '<i class="fa fa-circle" aria-hidden="true"></i>'
	else:
		max_html += '<i class="fa fa-arrow-circle-down" aria-hidden="true"></i>'

	min_html += '</small> <span class="fixed-width">' + str(min) + '%</span>'
	max_html += '</small> <span class="fixed-width">' + str(max) + '%</span>'

	icon = '<i class="fa fa-question-circle" aria-hidden="true" data-toggle="tooltip" title="The lifespan of ' + name + ' is between ' + str(
		min) + ' days and ' + str(
		max) + ' days; wild type lifespan is not available. Wild type lifespan was estimated to be between ' + str(
		organism_min_lifespan) + ' days and ' + str(
		organism_max_lifespan) + ' days (based on all data records in our db)"></i>'

	return mark_safe(
		icon + min_html + ' .. ' + max_html + ' ' + '<td class="est-column"><small class="text-muted">[est.]</small></td>')
