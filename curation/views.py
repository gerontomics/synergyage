from .forms import SubmitForm
from .models import Mutant, Lags, ModelInteractions, NewArticle, PubmedData, TissueExpression, Edges, Nodes, \
	GenePositions
from .utils import combs, split_string, mutant_type, randomize_positions, rearrange_nodes
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.management import call_command
from django.db.models import Q, F, Max, Min, Func, Value, Count
from django.db.models.functions import Lower
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from io import BytesIO
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as pyplot
from urllib.parse import urlencode
import collections
import json
import numpy
import io
import re
import urllib.request


def index(request):
	r_lifespans = Mutant.objects.filter(tax_id=6239).count()
	r_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=6239).order_by('genes').distinct(
		'genes').count()

	f_lifespans = Mutant.objects.filter(tax_id=7227).count()
	f_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=7227).order_by('genes').distinct(
		'genes').count()

	m_lifespans = Mutant.objects.filter(tax_id=10090).count()
	m_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=10090).order_by('genes').distinct(
		'genes').count()

	genetic_interventions = Mutant.objects.filter(genes__icontains=";").order_by('genes').distinct('genes').count()

	unique_genes = Lags.objects.filter().order_by('symbol').distinct('symbol').count()

	return render(request, 'curation/index.html',
	              {'r_combinations': r_combinations, 'r_lifespans': r_lifespans, 'f_combinations': f_combinations,
		              'f_lifespans': f_lifespans, 'm_combinations': m_combinations, 'm_lifespans': m_lifespans,
		              'genetic_interventions': genetic_interventions, 'unique_genes': unique_genes})


def about(request):
	return render(request, 'curation/about.html')


def download(request):
	with io.StringIO() as out:
		call_command('dumpdata', 'curation.Muutant', 'curation.ModelInteractions', stdout=out)
		data = out.getvalue()
	response = HttpResponse(content=data)
	response['Content-Type'] = 'application/json'
	response['Content-Disposition'] = 'attachment; filename="download.json"'
	return response


def methods(request):
	return render(request, 'curation/methods.html')


def browse(request):
	r_lifespans = Mutant.objects.filter(tax_id=6239).count()
	r_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=6239).order_by('genes').distinct(
		'genes').count()

	f_lifespans = Mutant.objects.filter(tax_id=7227).count()
	f_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=7227).order_by('genes').distinct(
		'genes').count()

	m_lifespans = Mutant.objects.filter(tax_id=10090).count()
	m_combinations = Mutant.objects.filter(genes__icontains=";", tax_id=10090).order_by('genes').distinct(
		'genes').count()

	return render(request, 'curation/browse.html',
	              {'r_combinations': r_combinations, 'r_lifespans': r_lifespans, 'f_combinations': f_combinations,
		              'f_lifespans': f_lifespans, 'm_combinations': m_combinations, 'm_lifespans': m_lifespans})


def search(request):
	# min & max for organism
	sql_min_max = ("select 1 as id, tax_id, max(lifespan) as max_lifespan, min(lifespan) as min_lifespan "
	               "from models "
	               "where genes = '-' "
	               "group by tax_id;")
	min_max_db = Mutant.objects.raw(sql_min_max)
	organism_min_lifespan = {}
	organism_max_lifespan = {}
	for data in min_max_db:
		organism_min_lifespan[data.tax_id] = data.min_lifespan
		organism_max_lifespan[data.tax_id] = data.max_lifespan

	# initial condition for queries
	initial_condition = Q()

	# order by condition
	orderby_condition = Lower('genes').asc()

	# If the form is submitted
	if request.method == 'POST':
		# filter
		post_filter = request.POST.get('filter')
		if post_filter == 'positive':
			initial_condition &= Q(effect__gte=5)
		elif post_filter == 'negative':
			initial_condition &= Q(effect__lt='-5')
		elif post_filter == 'small':
			initial_condition &= Q(effect__range=('-5', 5))

		# organism type
		organism_filter = request.POST.get('organism')
		if organism_filter != 'all':
			initial_condition &= Q(tax_id=organism_filter)

		# type of mutants filter
		included_types = []
		include_filter = request.POST.getlist('include')
		for filter in include_filter:
			included_types.append(filter)
		extra_where_condition = "(CHAR_LENGTH(genes) - CHAR_LENGTH(REPLACE(genes, ';', ''))) / CHAR_LENGTH(';') IN (" + ','.join(
			included_types) + ")"

		# order
		post_order = request.POST.get('order')
		if post_order == 'name_desc':
			orderby_condition = Lower('genes').desc()
		elif post_order == 'effect_asc':
			orderby_condition = F('max_effect').asc(nulls_last=True)
		elif post_order == 'effect_desc':
			orderby_condition = F('max_effect').desc(nulls_last=True)

		post_genes = request.POST.get('gene')
		# sort genes
		sorted_genes = []
		for gene in split_string(post_genes):
			sorted_genes.append(gene)

		# return all genes when searching for 'empty'
		if (sorted_genes[0] == 'empty'):
			sorted_genes[0] = ''

		sorted_genes = sorted(sorted_genes, key=lambda s: s.casefold())
		sorted_genes_string = ';'.join(sorted_genes)

		# no of genes
		total_genes = len(sorted_genes)

		# combinations and subcombinations
		combinations = combs(sorted_genes)
		subcombinations = []
		for combination in combinations:
			length = len(combination)
			if length > 1 and length < total_genes:
				subcombinations.append(combination)

		# initial condition. species ID and filter (if exists)
		q_exactMatch = initial_condition
		q_everyGene = initial_condition
		q_subcombs = initial_condition
		q_includeAll = initial_condition
		q_includeOne = initial_condition

		# exact match
		q_exactMatch &= Q(genes_name__iexact=sorted_genes_string)

		# subcombinations
		a_subcombs = Q()
		if subcombinations:
			for subcombination in subcombinations:
				a_subcombs |= Q(genes_name__iexact=';'.join(subcombination))
			q_subcombs &= a_subcombs
		# fix no subcombs
		else:
			q_subcombs &= Q(id__exact=0)

		# here we store OR conditions and then include them with AND
		a_everyGene = Q()
		a_includeOne = Q()

		for gene in sorted_genes:
			if gene != '':
				# every gene
				a_everyGene |= Q(genes_name__icontains=gene)
				# combinations that include all genes & other genes
				q_includeAll &= Q(genes_name__icontains=gene + ';') | Q(genes_name__iendswith=gene)
				# combinations that include at least one gene & other genes
				a_includeOne |= Q(genes_name__icontains=gene + ';') | Q(genes_name__iendswith=gene)

		q_everyGene &= a_everyGene
		q_includeOne &= a_includeOne

		# genes_name annotate for every sql to improve search
		everyGene = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'), function='regexp_replace')).exclude(
			genes_name__contains=';').exclude(genes__iexact="-").order_by(orderby_condition).filter(q_everyGene).extra(
			where=[extra_where_condition])

		exactMatch = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'), function='regexp_replace')).exclude(
			pk__in=everyGene.values_list('pk', flat=True)).exclude(genes__iexact="-").order_by(
			orderby_condition).filter(q_exactMatch).extra(where=[extra_where_condition])

		subcombs = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).annotate(genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
		                                                function='regexp_replace')).order_by(orderby_condition).filter(
			q_subcombs).extra(where=[extra_where_condition])

		# includeAll prinde "all genes" atunci cand search-ul este gol.
		# excludem every gene in acest caz, pentru ca intra acolo single mutants
		if post_genes == '':
			exclude_every_gene = []
		else:
			exclude_every_gene = everyGene.values_list('pk', flat=True)

		includeAll = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).annotate(genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
		                                                function='regexp_replace')).order_by(orderby_condition).filter(
			q_includeAll).exclude(pk__in=exclude_every_gene).exclude(
			pk__in=exactMatch.values_list('pk', flat=True)).exclude(
			pk__in=subcombs.values_list('pk', flat=True)).exclude(genes=sorted_genes_string).exclude(
			genes__iexact="-").extra(where=[extra_where_condition])

		includeOne = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).annotate(genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
		                                                function='regexp_replace')).order_by(orderby_condition).filter(
			q_includeOne).exclude(pk__in=everyGene.values_list('pk', flat=True)).exclude(
			pk__in=exactMatch.values_list('pk', flat=True)).exclude(
			pk__in=includeAll.values_list('pk', flat=True)).exclude(
			pk__in=subcombs.values_list('pk', flat=True)).exclude(genes__iexact="-").extra(
			where=[extra_where_condition])

		context = {'genes': sorted_genes, 'exactMatch': exactMatch, 'everyGene': everyGene, 'subcombs': subcombs,
		           'includeAll': includeAll, 'includeOne': includeOne, 'included_types': included_types,
		           'organism_min_lifespan': organism_min_lifespan, 'organism_max_lifespan': organism_max_lifespan}
	else:
		# hide single mutants
		initial_condition &= Q(genes__contains=';')
		genes = Mutant.objects.values('genes', 'tax_id').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			tax=Max('tax_id')).order_by(orderby_condition).filter(initial_condition).exclude(genes__iexact="-")
		paginator = Paginator(genes, 50)  # Show 50 genes per page

		no_genes = genes.count()

		page = request.GET.get('page')
		try:
			allGenes = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			allGenes = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			allGenes = paginator.page(paginator.num_pages)

		context = {'allGenes': allGenes, 'no_genes': no_genes, 'organism_min_lifespan': organism_min_lifespan,
		           'organism_max_lifespan': organism_max_lifespan}

	return render(request, 'curation/search.html', context)


def submit_article(request):
	# If the form is submitted
	if request.POST:
		form = SubmitForm(request.POST)
		if form.is_valid():
			# Check if captcha is valid
			recaptcha_response = request.POST.get('g-recaptcha-response')
			url = 'https://www.google.com/recaptcha/api/siteverify'
			values = {'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY, 'response': recaptcha_response}
			data = urlencode(values).encode()
			req = urllib.request.Request(url, data=data)
			response = urllib.request.urlopen(req)
			result = json.loads(response.read().decode())
			if result['success']:
				pubmed = request.POST.get('pubmed')
				citation = request.POST.get('citation')
				email = request.POST.get('email')
				description = request.POST.get('description')
				type = request.POST.get('type')
				if email:
					# Check if email is valid
					match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email)
					if match == None:
						context = {'form': form, 'error': 'Invalid email address.'}
					else:
						# it's PubMed
						if type == '1':
							if pubmed.isdigit():
								if Mutant.objects.filter(pmid=pubmed).exists():
									context = {'form': form, 'error': 'This article is already in our database.'}
								else:
									if NewArticle.objects.filter(pmid=pubmed).exists():
										context = {'form': form, 'error': 'This article was already suggested.'}
									else:
										pubmed_html = urllib.request.urlopen(
											'https://www.ncbi.nlm.nih.gov/pubmed/?term=' + pubmed).read()
										soup = BeautifulSoup(pubmed_html, "html.parser")
										# Now we can get the title of the PubMed site from the soup variable
										title = soup.title.string.strip()
										if title == 'No items found - PubMed - NCBI':
											context = {'form': form, 'error': 'Invalid PubMed ID.'}
										else:
											# Process form data
											article = NewArticle()
											article.pmid = pubmed
											article.email = email
											article.description = description
											# Save the object in database for model "NewArticle"
											article.save()
											# Process form data
											'''
											data = CuurationData()
											data.pmid = pubmed
											data.double_mutant_lifespan = 0
											data.single_mutant_1_lifespan = 0
											data.single_mutant_2_lifespan = 0
											data.temperature = 0
											# Save the object in database for model "NewArticle"
											data.save()
											'''
											context = {'form': form, 'success': "Thank you! We'll review your article."}
							else:
								context = {'form': form, 'error': 'PubMed ID must be numeric.'}
						# it's manual citation'
						if type == '2':
							if citation:
								# Process form data
								article = NewArticle()
								article.citation = citation
								article.email = email
								article.description = description
								# Save the object in database for model "NewArticle"
								article.save()
								context = {'form': form, 'success': "Thank you! We'll review your citation."}
							else:
								context = {'form': form, 'error': 'Please complete citation.'}
				else:
					context = {'form': form, 'error': 'Please complete email address.'}
			else:
				context = {'form': form, 'error': 'Invalid captcha.', 'context': result}
		else:
			context = {'form': form, 'error': 'Invalid form, try again.'}
	else:
		form = SubmitForm()
		context = {'form': form}

	return render(request, 'curation/submit-article.html', context)


def browse_species(request, species_id):
	# initial condition for queries
	initial_condition = Q(tax_id=species_id)
	exclude_condition = Q()

	# species
	if species_id == 6239:
		tax_name = 'Roundworm'
	elif species_id == 7227:
		tax_name = 'Fruit fly'
	elif species_id == 10090:
		tax_name = 'Mouse'

	# min & max for organism
	sql_min_max = ("select 1 as id, max(lifespan) as max_lifespan, min(lifespan) as min_lifespan "
	               "from models "
	               "where genes = '-' "
	               "and tax_id = " + str(species_id) + ";")
	min_max_db = Mutant.objects.raw(sql_min_max)
	organism_lifespan = [min_max_db[0].min_lifespan, min_max_db[0].max_lifespan]

	# order by condition
	orderby_condition = Lower('genes').asc()

	# If the form is submitted
	if request.method == 'POST':
		# filter
		post_filter = request.POST.get('filter')
		if post_filter == 'positive':
			initial_condition &= Q(effect__gte=5)
		elif post_filter == 'negative':
			initial_condition &= Q(effect__lt='-5')
		elif post_filter == 'small':
			initial_condition &= Q(effect__range=('-5', 5))

		# incomplete data
		incomplete_filter = request.POST.get('incomplete')
		if not incomplete_filter:
			exclude_condition &= Q(interaction_type__isnull=True) & Q(genes_name__contains=';')

		# type of mutants filter
		included_types = []
		include_filter = request.POST.getlist('include')
		for filter in include_filter:
			included_types.append(filter)
		extra_where_condition = "(CHAR_LENGTH(genes) - CHAR_LENGTH(REPLACE(genes, ';', ''))) / CHAR_LENGTH(';') IN (" + ','.join(
			included_types) + ")"

		# order
		post_order = request.POST.get('order')
		if post_order == 'name_desc':
			orderby_condition = Lower('genes').desc()
		elif post_order == 'effect_asc':
			orderby_condition = F('max_effect').asc(nulls_last=True)
		elif post_order == 'effect_desc':
			orderby_condition = F('max_effect').desc(nulls_last=True)

		post_genes = request.POST.get('gene')
		# sort genes
		sorted_genes = []
		for gene in split_string(post_genes):
			sorted_genes.append(gene)

		# return all genes when searching for 'empty'
		if (sorted_genes[0] == 'empty'):
			sorted_genes[0] = ''

		sorted_genes = sorted(sorted_genes, key=lambda s: s.casefold())
		sorted_genes_string = ';'.join(sorted_genes)

		# no of genes
		total_genes = len(sorted_genes)

		# combinations and subcombinations
		combinations = combs(sorted_genes)
		subcombinations = []
		for combination in combinations:
			length = len(combination)
			if length > 1 and length < total_genes:
				subcombinations.append(combination)

		# initial condition. species ID and filter (if exists)
		q_exactMatch = initial_condition
		q_everyGene = initial_condition
		q_subcombs = initial_condition
		q_includeAll = initial_condition
		q_includeOne = initial_condition

		# exact match
		q_exactMatch &= Q(genes_name__iexact=sorted_genes_string)

		# subcombinations
		a_subcombs = Q()
		if subcombinations:
			for subcombination in subcombinations:
				a_subcombs |= Q(genes_name__iexact=';'.join(subcombination))
			q_subcombs &= a_subcombs
		# fix no subcombs
		else:
			q_subcombs &= Q(id__exact=0)

		# here we store OR conditions and then include them with AND
		a_everyGene = Q()
		a_includeOne = Q()

		for gene in sorted_genes:
			if gene != '':
				# every gene
				a_everyGene |= Q(genes_name__icontains=gene)
				# combinations that include all genes & other genes
				q_includeAll &= Q(genes_name__icontains=gene + ';') | Q(genes_name__iendswith=gene)
				# combinations that include at least one gene & other genes
				a_includeOne |= Q(genes_name__icontains=gene + ';') | Q(genes_name__iendswith=gene)

		q_everyGene &= a_everyGene
		q_includeOne &= a_includeOne

		# genes_name annotate for every sql to improve search
		everyGene = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'), function='regexp_replace')).exclude(
			genes_name__contains=';').exclude(genes__iexact="-").order_by(orderby_condition).filter(
			q_everyGene).exclude(exclude_condition).extra(where=[extra_where_condition])

		exactMatch = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'), function='regexp_replace')).exclude(
			pk__in=everyGene.values_list('pk', flat=True)).exclude(genes__iexact="-").order_by(
			orderby_condition).filter(q_exactMatch).exclude(exclude_condition).extra(where=[extra_where_condition])

		subcombs = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
			                function='regexp_replace')).order_by(orderby_condition).filter(q_subcombs).exclude(
			exclude_condition).extra(where=[extra_where_condition])

		# includeAll prinde "all genes" atunci cand search-ul este gol.
		# excludem every gene in acest caz, pentru ca intra acolo single mutants
		if post_genes == '':
			exclude_every_gene = []
		else:
			exclude_every_gene = everyGene.values_list('pk', flat=True)

		includeAll = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
			                function='regexp_replace')).order_by(orderby_condition).filter(q_includeAll).exclude(
			pk__in=exclude_every_gene).exclude(pk__in=exactMatch.values_list('pk', flat=True)).exclude(
			pk__in=subcombs.values_list('pk', flat=True)).exclude(genes=sorted_genes_string).exclude(
			genes__iexact="-").exclude(exclude_condition).extra(where=[extra_where_condition])

		includeOne = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).annotate(
			genes_name=Func(F('genes'), Value('[^A-z0-9;]'), Value(''), Value('g'),
			                function='regexp_replace')).order_by(orderby_condition).filter(q_includeOne).exclude(
			pk__in=everyGene.values_list('pk', flat=True)).exclude(
			pk__in=exactMatch.values_list('pk', flat=True)).exclude(
			pk__in=includeAll.values_list('pk', flat=True)).exclude(
			pk__in=subcombs.values_list('pk', flat=True)).exclude(genes__iexact="-").exclude(exclude_condition).extra(
			where=[extra_where_condition])

		context = {'tax_name': tax_name, 'genes': sorted_genes, 'exactMatch': exactMatch, 'everyGene': everyGene,
		           'subcombs': subcombs, 'includeAll': includeAll, 'includeOne': includeOne, 'species_id': species_id,
		           'included_types': included_types, 'organism_lifespan': organism_lifespan}
	else:
		# hide single mutants
		initial_condition &= Q(genes__contains=';')
		genes = Mutant.objects.values('genes').annotate(max_effect=Max('effect')).annotate(
			min_effect=Min('effect')).annotate(max_lifespan=Max('lifespan')).annotate(
			min_lifespan=Min('lifespan')).annotate(count=Count('id')).annotate(id=Max('id')).order_by(
			orderby_condition).filter(initial_condition).exclude(genes__iexact="-").exclude(exclude_condition)
		paginator = Paginator(genes, 50)  # Show 50 genes per page

		no_genes = genes.count()

		page = request.GET.get('page')
		try:
			allGenes = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			allGenes = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			allGenes = paginator.page(paginator.num_pages)

		context = {'tax_name': tax_name, 'allGenes': allGenes, 'no_genes': no_genes, 'species_id': species_id,
		           'organism_lifespan': organism_lifespan}

	return render(request, 'curation/browse_species.html', context)


def details(request, id):
	# find model for received ID
	t_model = Mutant.objects.filter(id=id)[0]

	# genes for model
	genes = t_model.genes.split(';')

	# keep only different genes. sometimes we have daf-2;sod-2;sod-2 (eg. 1117).
	# genes = list(set(genes))

	# sort genes
	sorted_genes = []
	for gene in genes:
		# remove spaces for every gene
		gene = gene.replace(" ", "")
		sorted_genes.append(gene)
	sorted_genes = sorted(sorted_genes, key=lambda s: s.casefold())
	sorted_genes_string = ';'.join(sorted_genes)

	# update t_model to avoid duplicate genes in template
	# t_model.genes = ';'.join(genes)

	# comma enumeration genes
	comma_genes = t_model.genes.replace(";", ", ")

	condition = Q(tax_id=t_model.tax_id)
	condition &= Q(genes__iexact=sorted_genes_string)
	models = Mutant.objects.filter(condition).distinct('id')

	for model in models:
		model.modelinteractions = ModelInteractions.objects.filter(id2=model.id, ).exclude(comm__isnull=True).exclude(
			comm='').first()

		# PubMed data
		pubmed = PubmedData.objects.filter(pmid=model.pmid)
		if pubmed:
			model.citation = pubmed[0].citation
			model.abstract = pubmed[0].abstract
		else:
			# get html source for current PubMed ID
			pubmed_html = urllib.request.urlopen("https://www.ncbi.nlm.nih.gov/pubmed/?term=" + str(model.pmid)).read()
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
			# abstract
			abstract_html = soup.find("div", {"class": "abstr"})
			if abstract_html:
				abstract = abstract_html.find("p").contents[0]
			else:
				abstract = ""

			# title
			title = soup.find("h1", {"class": ""}).get_text()

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

			citation = authors + ', ' + year + ', ' + title + ' ' + issue + ' ' + number + ':' + pages

			model.citation = citation
			model.abstract = abstract
			# also, store PubMed data in database to be used next time
			pubmed_data = PubmedData()
			pubmed_data.pmid = model.pmid
			pubmed_data.citation = citation
			pubmed_data.abstract = abstract
			pubmed_data.save()

	# (top section) info for every gene
	results = []
	for gene in genes:
		# sometimes we have "daf-16; daf-2"
		gene = gene.strip()
		# get data where symbol match exact gene name
		data = Lags.objects.filter(symbol=gene).filter(tax_id=t_model.tax_id)
		if len(data) < 1:
			data = {}
			data[gene] = gene
		results.extend(data)

	# two graphs
	count_small_graph = ModelInteractions.objects.raw(
		"select 1 as id1, count(*) as c from curation_modelinteractions where id2 in (select id from models where genes = '" + t_model.genes + "');")
	count_big_graph = ModelInteractions.objects.raw(
		"select 1 as id1, count(*) as c from curation_modelinteractions where id1 in (select id from models where genes = '" + t_model.genes + "');")

	context = {'t_model': t_model, 'models': models, 'results': results, 'genes': genes, 'comma_genes': comma_genes,
		'count_small_graph': count_small_graph[0].c, 'count_big_graph': count_big_graph[0].c}

	return render(request, 'curation/details.html', context)


def wildtype(request):
	temperatures = []

	histograms = []
	temps = Mutant.objects.raw(
		"select 1 as id, count(lifespan) as count, temp from models where tax_id = 6239 and name = 'wild type' and temp not in ('', 'NA') group by temp;")
	for temp in temps:
		if temp.count > 9:
			lifespans = Mutant.objects.raw(
				"select 1 as id, temp, lifespan from models where tax_id = 6239 and name = 'wild type' and temp = '" + temp.temp + "';")
			values = []
			for lifespan in lifespans:
				values.append(lifespan.lifespan)
			temps = [temp.temp]
			temperatures.append(temp.temp)
			temps.append(values)
			histograms.append(temps)

	# count entries for temperatures
	count_entries = Mutant.objects.filter(temp__in=temperatures).filter(tax_id=6239).count()
	# count undetermined
	count_undet = Mutant.objects.filter(temp__in=['', 'NA']).filter(tax_id=6239).count()

	# table
	results = Mutant.objects.raw(
		"select 1 as id, count(temp) as count, temp from models where tax_id = 6239 and name = 'wild type' and temp not in ('', 'NA') group by temp;")

	context = {'temperatures': temperatures, 'count_entries': count_entries, 'count_undet': count_undet,
		'results': results, 'histograms': histograms}

	return render(request, 'curation/wildtype.html', context)


def expTable(request):
	name = request.GET.get('name', None)

	# here we store given positions (at the time checked)
	positions = {}

	model_type = mutant_type(name)

	if model_type == 'single':
		sql = (
					"SELECT m.id, e.id_exp, m.name, m.lifespan, CASE WHEN m.name = 'wild type' THEN -1 ELSE ROUND((LENGTH(m.name) - LENGTH(REPLACE(m.name, ';', ''))) / LENGTH(';')) END AS count "
					"FROM models m "
					"JOIN experiments e ON e.id_model = m.id WHERE e.id_exp IN (SELECT id_exp FROM models m JOIN experiments e ON e.id_model = m.id WHERE m.name = '" + name + "') AND (m.name LIKE '%%" + name + "%%' OR m.genes = '-') ORDER BY e.id_exp, count, name;")
	elif model_type == 'double':
		sql = (
					"SELECT m.id, e.id_exp, m.name, m.lifespan, CASE WHEN m.name = 'wild type' THEN -1 ELSE ROUND((LENGTH(m.name) - LENGTH(REPLACE(m.name, ';', ''))) / LENGTH(';')) END AS count "
					"FROM models m "
					"JOIN experiments e ON e.id_model = m.id WHERE id_exp IN (SELECT t1.id_exp FROM (SELECT id_exp FROM models m JOIN experiments e ON e.id_model = m.id WHERE m.name = '" + name + "') t1 JOIN (SELECT id_exp, MAX(ROUND((LENGTH(m.name) - LENGTH(REPLACE(m.name, ';', ''))) / LENGTH(';'))) FROM models m JOIN experiments e ON e.id_model = m.id GROUP BY id_exp HAVING MAX(ROUND((LENGTH(m.name) - LENGTH(REPLACE(m.name, ';', ''))) / LENGTH(';'))) < 2) t2 ON t1.id_exp = t2.id_exp) ORDER BY e.id_exp, count, name;")
	else:
		sql = (
					"SELECT m.id, e.id_exp, m.name, m.lifespan, CASE WHEN m.name = 'wild type' THEN -1 ELSE ROUND((LENGTH(m.name) - LENGTH(REPLACE(m.name, ';', ''))) / LENGTH(';')) END AS count "
					"FROM models m "
					"JOIN experiments e ON e.id_model = m.id WHERE e.id_exp IN (SELECT id_exp FROM models m JOIN experiments e ON e.id_model = m.id WHERE m.name = '" + name + "') ORDER BY e.id_exp, count, name;")
	experiments_obj = Mutant.objects.raw(sql)

	experiments = collections.defaultdict(list)

	for experiment in experiments_obj:

		if experiment.id_exp not in positions.keys():
			positions[experiment.id_exp] = []

		type = mutant_type(experiment.name)

		if type == 'wildtype':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 0
		elif type == 'single':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 1
		elif type == 'double':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 2
		elif type == 'triple':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 3
		elif type == 'quadruple':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 4
		elif type == 'quintuple':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 5
		elif type == 'sextuple':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 6
		elif type == 'rest':
			try:
				order = positions[experiment.id_exp][-1] + 1
			except IndexError:
				order = 7

		positions[experiment.id_exp].append(order)

		experiments[experiment.id_exp].append([experiment.name, experiment.lifespan, order])

	return JsonResponse(experiments)


def keggInfo(request):
	name = request.GET.get('name', None)
	path = request.GET.get('path', None)
	tax_id = request.GET.get('tax_id', None)

	result = {}
	result['data'] = []

	if name:
		sql = ("select l.entrez_id, map.path_id, kegg.path_name "
		       "from lags l "
		       "inner join kegg_mapping_cel map "
		       "on l.entrez_id = map.entrez_id "
		       "inner join kegg_cel kegg "
		       "on map.path_id = kegg.path_id "
		       "where l.symbol = '" + name + "' "
		                                     "group by l.entrez_id,  map.path_id, kegg.path_name;")
		data = Lags.objects.raw(sql)
		for kegg in data:
			result['data'].append([kegg.path_id, kegg.path_name])

	elif path:
		sql = ("select l.symbol, l.entrez_id "
		       "from kegg_mapping_cel map "
		       "inner join lags l "
		       "on map.entrez_id = l.entrez_id "
		       "where map.path_id = '" + path + "' "
		                                        "group by l.symbol, l.entrez_id;")
		data = Lags.objects.raw(sql)
		for lag in data:
			result['data'].append([lag.symbol])

	else:
		sql = ("select distinct on (lower(kegg.path_name)) l.entrez_id, map.path_id, kegg.path_name "
		       "from lags l "
		       "inner join kegg_mapping_cel map "
		       "on l.entrez_id = map.entrez_id "
		       "inner join kegg_cel kegg "
		       "on map.path_id = kegg.path_id "
		       "where l.tax_id = '" + tax_id + "' "
		                                       "order by lower(kegg.path_name) asc;")
		data = Lags.objects.raw(sql)
		for kegg in data:
			result['data'].append([kegg.path_id, kegg.path_name])

	return JsonResponse(result)


def tissue_expression(request):
	name = request.GET.get('name', None)
	tissue = request.GET.get('tissue', None)

	result = {}
	result['data'] = []

	if name:
		sql = ("select t.tissue, t.entrez_id "
		       "from tissue_expression t "
		       "inner join lags l "
		       "on l.entrez_id = t.entrez_id "
		       "where l.symbol = '" + name + "' "
		                                     "group by t.tissue, t.entrez_id;")
		data = TissueExpression.objects.raw(sql)
		for value in data:
			result['data'].append([value.tissue])

	elif tissue:
		sql = ("select l.symbol, l.entrez_id "
		       "from tissue_expression t "
		       "inner join lags l "
		       "on t.entrez_id = l.entrez_id "
		       "where t.tissue = '" + tissue + "' "
		                                       "group by l.symbol, l.entrez_id;")
		data = TissueExpression.objects.raw(sql)
		for value in data:
			result['data'].append([value.symbol])

	return JsonResponse(result)


def type_of_interaction(request):
	gene_names = request.POST.getlist('gene_names[]')

	types = collections.defaultdict(list)

	if gene_names:
		sql = ("select 1 as id, genes, interaction_type, count(interaction_type) as count, max(effect) as effect "
		       "from models "
		       "where genes in ('" + "','".join(gene_names) + "') and interaction_type is not null "
		                                                      "group by genes, interaction_type "
		                                                      "order by genes, interaction_type desc;")
		data = Mutant.objects.raw(sql)

		for type in data:
			types[type.genes].append([type.interaction_type, type.count, type.effect])

	result = {'result': types}

	return JsonResponse(result)


def graphData(request):
	type = request.GET.get('type', None)
	tax_id = request.GET.get('tax_id', None)
	page_id = request.GET.get('page_id', None)

	organism_coefficient = {'6239': 1, '7227': 1, '10090': 10}
	coefficient = organism_coefficient[tax_id]

	# min and max lifespan
	# everytime we have at least one lifespan smaller than 999?
	min_lifespan = 999
	# everytime we have at least one lifespan bigger than 0?
	max_lifespan = 0

	min_x_position = 0
	original_max_x_position = 4000

	response_data = {}
	response_data['positions'] = []

	sql_max_lifespan = ("select 1 as id, max(lifespan) as max_lifespan from models where tax_id = " + tax_id)
	max_lifespan_db = Mutant.objects.raw(sql_max_lifespan)
	max_lifespan_point = 0
	for value in max_lifespan_db:
		max_lifespan_point = value.max_lifespan

	sql_min_lifespan = ("select 1 as id, min(lifespan) as min_lifespan from models where tax_id = " + tax_id)
	min_lifespan_db = Mutant.objects.raw(sql_min_lifespan)
	min_lifespan_point = 0
	for value in min_lifespan_db:
		min_lifespan_point = value.min_lifespan

	# new positions
	new_positions = {}
	new_positions_queryset = GenePositions.objects.filter(page_id=page_id, small_big=type).values('page_id', 'genes',
	                                                                                              'x_position')
	for position in new_positions_queryset:
		new_positions[position['genes']] = position['x_position']

	# extra nodes
	extra_nodes = []
	extra_edges = []
	nodes_sql = (
				"select distinct on(n.page_id, n.node_id) n.page_id, n.node_id, m.lifespan, m.name, m.temp, m.pmid, n.x_position, n.y_position, 1 as id from nodes n inner join models m on n.node_id = m.id where n.page_id = " + str(
			page_id) + " and n.small_big = '" + type + "';")
	extra_nodes_queryset = Nodes.objects.raw(nodes_sql)

	max_x_position = 0

	if type == 'big':
		# max_x_position it's rewritten
		original_max_x_position = max_x_position

	for node in extra_nodes_queryset:
		if node.x_position > max_x_position:
			max_x_position = node.x_position

		extra_nodes.append(
			{'page_id': node.page_id, 'node_id': node.node_id, 'lifespan': node.lifespan, 'name': node.name,
				'temperature': node.temp, 'pmid': node.pmid, 'x_position': node.x_position,
				'y_position': node.y_position})
	extra_edges_queryset = Edges.objects.filter(page_id=page_id, small_big=type).values('page_id', 'id1', 'id2')
	for edge in extra_edges_queryset:
		extra_edges.append({'page_id': edge['page_id'], 'id1': edge['id1'], 'id2': edge['id2']})

	response_data['lifespan'] = (
	{'min_position': (200 - min_lifespan * 15) / coefficient, 'min_lifespan': min_lifespan / coefficient,
		'max_position': (200 - max_lifespan * 15) / coefficient, 'max_lifespan': max_lifespan / coefficient,
		'max_lifespan_point': (200 - max_lifespan_point * 15) / coefficient,
		'min_lifespan_point': (200 - min_lifespan_point * 15) / coefficient,
		'max_lifespan_point_value': max_lifespan_point, 'min_lifespan_point_value': min_lifespan_point,
		'x': min_x_position - 100, 'y': max_x_position})

	for name, x_position in new_positions.items():
		if name == '-': name = 'wild type'
		if type != 'big' and x_position <= original_max_x_position:
			response_data['positions'].append({'name': name, 'x_position': x_position})
		elif type == 'big' and x_position < original_max_x_position:
			response_data['positions'].append({'name': name, 'x_position': x_position})

	if type == 'big':
		response_data['positions'].append({'name': 'multiple mutants', 'x_position': original_max_x_position})

	response_data['extra_points'] = [{'nodes': extra_nodes, 'edges': extra_edges, }]

	return JsonResponse(response_data)


def histogram(request):
	data = [float(val) for val in request.GET['data'].split(',')]
	binwidth = 0.5

	fig, ax = pyplot.subplots()

	ax.hist(data, bins=numpy.arange(min(data), max(data) + binwidth, binwidth))
	ax.set_title('Distribution of wildtype lifespans at ' + request.GET['temp'] + '°C')
	ax.set_xlabel('Lifespan (days)')
	ax.set_ylabel('Number of worms')

	f = BytesIO()

	pyplot.savefig(f, format='png')
	pyplot.clf()
	pyplot.close(fig)

	return HttpResponse(f.getvalue(), content_type='image/png')
