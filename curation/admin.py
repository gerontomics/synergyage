from django.contrib import admin

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.shortcuts import redirect

# Register your models here.
from .models import NewArticle, Lags, Mutant, ModelInteractions, Approve, Muutant, CurationData, PubmedData

import urllib.request
import re
from bs4 import BeautifulSoup


class ArticleAdmin(admin.ModelAdmin):
	list_display = ('pmid', 'citation', 'state', 'email', 'description', 'created_at',)
	list_editable = ('citation', 'state',)
	list_filter = ['state']

	change_form_template = 'admin/curation/article/change_form.html'

	def change_view(self, request, object_id, form_url='', extra_context=None):
		# get pmid for current ID
		article = NewArticle.objects.filter(id=object_id).first()

		# get html source for current PubMed ID
		pubmed_html = urllib.request.urlopen("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(article.pmid)).read()
		soup = BeautifulSoup(pubmed_html, "html.parser")

		# authors
		authors = []
		authors_html = soup.find("div", {"class": "auths"})
		for author in authors_html.find_all("a"):
			# use "string" because they're links
			authors.append(author.string)
		if len(authors) >= 3:
			authors = authors[0] + " et al."
		else:
			authors = ', '.join(authors)

		# title
		title = soup.find("h1", {"class": ""}).string

		# abstract
		if soup.find("abstracttext"):
			abstract = soup.find("abstracttext").string
		else:
			abstract = "No abstract"

		# issue
		issue = soup.find("a", {"alsec": "jour"}).string

		# issue and page html
		# [0] is issue with link
		issueandpage_html = soup.find("div", {"class": "cit"}).contents[1].strip()

		# issue year
		year = issueandpage_html.split(" ")[0]

		# issue number
		regex = re.compile(';(.*?):')  # between ; and :
		search = regex.search(issueandpage_html)
		number = search.group(1)

		# issue pages
		regex = re.compile(':(.*?)\.')  # between : and . (escaped with \)
		search = regex.search(issueandpage_html)
		pages = search.group(1)

		extra_context = extra_context or {}
		extra_context['pmid'] = article.pmid
		extra_context['authors'] = authors
		extra_context['title'] = title
		extra_context['abstract'] = abstract
		extra_context['issue'] = issue
		extra_context['year'] = year
		extra_context['number'] = number
		extra_context['pages'] = pages
		return super(ArticleAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context, )

	def response_change(self, request, obj):
		if (obj.state == '1'):
			url = '/admin/curation/curationdata/add/?pmid=' + str(obj.pmid)
		else:
			url = '/admin/curation/article/'
		return redirect(url)


admin.site.register(NewArticle, ArticleAdmin)

admin.site.register(Lags)
admin.site.register(Mutant)
admin.site.register(PubmedData)


class ApproveAdmin(admin.ModelAdmin):
	change_form_template = 'admin/curation/approve/change_form.html'

	def add_view(self, request, form_url='', extra_context=None):
		extra_context = extra_context or {}
		if request.method == 'GET' and 'pmid' in request.GET:
			# get PubMed ID from $_GET
			pmid = request.GET.get('pmid');

			# get html source for current PubMed ID
			pubmed_html = urllib.request.urlopen("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(pmid)).read()
			soup = BeautifulSoup(pubmed_html, "html.parser")

			# authors
			authors = []
			authors_html = soup.find("div", {"class": "auths"})
			for author in authors_html.find_all("a"):
				# use "string" because they're links
				authors.append(author.string)
			if len(authors) >= 3:
				authors = authors[0] + " et al."
			else:
				authors = ', '.join(authors)

			# title
			title = soup.find("h1", {"class": ""}).string

			# abstract
			if soup.find("abstracttext"):
				abstract = soup.find("abstracttext").string
			else:
				abstract = "No abstract"

			# issue
			issue = soup.find("a", {"alsec": "jour"}).string

			# issue and page html
			# [0] is issue with link
			issueandpage_html = soup.find("div", {"class": "cit"}).contents[1].strip()

			# issue year
			year = issueandpage_html.split(" ")[0]

			# issue number
			regex = re.compile(';(.*?):')  # between ; and :
			search = regex.search(issueandpage_html)
			number = search.group(1)

			# issue pages
			regex = re.compile(':(.*?)\.')  # between : and . (escaped with \)
			search = regex.search(issueandpage_html)
			pages = search.group(1)

			extra_context['pmid'] = pmid
			extra_context['authors'] = authors
			extra_context['title'] = title
			extra_context['abstract'] = abstract
			extra_context['issue'] = issue
			extra_context['year'] = year
			extra_context['number'] = number
			extra_context['pages'] = pages
		else:
			extra_context['pmid'] = '';
		return super(ApproveAdmin, self).add_view(request, form_url, extra_context=extra_context, )


admin.site.register(Approve, ApproveAdmin)


class ModelInteractionsAdmin(admin.ModelAdmin):
	list_display = ('id1', 'id2',)


admin.site.register(ModelInteractions, ModelInteractionsAdmin)

# new models
admin.site.register(Muutant)


# inline for mutants
class MuutantInline(admin.TabularInline):
	model = CurationData.mutant.through

	# no extra fields, only used ones
	extra = 1

	# fields = [
	#     'muutant_model_name',
	#     'muutant_parent',
	#     'muutant_entrez_id',
	#     'muutant_intervention',
	#     'muutant_temperature',
	#     'muutant_diet',
	#     'muutant_lifespan',
	#     'muutant_calorically_restricted',
	#     'muutant_composite_id'
	# ]

	readonly_fields = ['muutant_model_name', 'muutant_parent', 'muutant_entrez_id', 'muutant_intervention',
		'muutant_temperature', 'muutant_diet', 'muutant_lifespan', 'muutant_calorically_restricted',
		'muutant_composite_id']

	def muutant_parent(self, instance):
		return instance.muutant.tempemuutant_parentrature

	def muutant_entrez_id(self, instance):
		return instance.muutant.entrez_id

	def muutant_intervention(self, instance):
		return instance.muutant.intervention

	def muutant_temperature(self, instance):
		return instance.muutant.temperature

	def muutant_diet(self, instance):
		return instance.muutant.diet

	def muutant_lifespan(self, instance):
		return instance.muutant.lifespan

	def muutant_calorically_restricted(self, instance):
		return instance.muutant.calorically_restricted

	def muutant_model_name(self, instance):
		return instance.muutant.model_name

	def muutant_composite_id(self, instance):
		return instance.muutant.composite_id


# all the magic
class CurationDataAdmin(admin.ModelAdmin):
	# show fields mentioned before
	inlines = [MuutantInline, ]

	# avoid duplicate
	exclude = ('mutant',)

	# used for PubMed ID
	change_form_template = 'admin/curation/curationdata/change_form.html'

	# this works, except for inline...

	# def formfield_for_manytomany(self, db_field, request, **kwargs):
	#     if db_field.name == "mutant":
	#         kwargs["queryset"] = Muutant.objects.filter(pmid=321)
	#     return super(CurationDataAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

	def add_view(self, request, form_url='', extra_context=None):
		extra_context = extra_context or {}
		# get PubMed ID from $_GET
		pmid = request.GET.get('pmid');

		# get html source for current PubMed ID
		pubmed_html = urllib.request.urlopen("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(pmid)).read()
		soup = BeautifulSoup(pubmed_html, "html.parser")

		# authors
		authors = []
		authors_html = soup.find("div", {"class": "auths"})
		for author in authors_html.find_all("a"):
			# use "string" because they're links
			authors.append(author.string)
		if len(authors) >= 3:
			authors = authors[0] + " et al."
		else:
			authors = ', '.join(authors)

		# title
		title = soup.find("h1", {"class": ""}).string

		# abstract
		if soup.find("abstracttext"):
			abstract = soup.find("abstracttext").string
		else:
			abstract = "No abstract"

		# issue
		issue = soup.find("a", {"alsec": "jour"}).string

		# issue and page html
		# [0] is issue with link
		issueandpage_html = soup.find("div", {"class": "cit"}).contents[1].strip()

		# issue year
		year = issueandpage_html.split(" ")[0]

		# issue number
		regex = re.compile(';(.*?):')  # between ; and :
		search = regex.search(issueandpage_html)
		number = search.group(1)

		# issue pages
		regex = re.compile(':(.*?)\.')  # between : and . (escaped with \)
		search = regex.search(issueandpage_html)
		pages = search.group(1)

		extra_context['pmid'] = pmid
		extra_context['authors'] = authors
		extra_context['title'] = title
		extra_context['abstract'] = abstract
		extra_context['issue'] = issue
		extra_context['year'] = year
		extra_context['number'] = number
		extra_context['pages'] = pages

		return super(CurationDataAdmin, self).add_view(request, form_url, extra_context=extra_context, )


admin.site.register(CurationData, CurationDataAdmin)
