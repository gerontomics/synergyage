import itertools, re, random


def combs(items):
	return itertools.chain.from_iterable(itertools.combinations(items, i + 1) for i in range(len(items)))


def distinct_genes(model, species_id):
	distinct_genes = []

	genes = model.objects.filter(tax_id=species_id).exclude(genes__iexact="-")

	for gene in genes:
		for g in gene.genes.split(';'):
			if g not in distinct_genes:
				distinct_genes.append(g)

	return len(distinct_genes)


def split_string(x):
	x = re.sub('[^0-9A-z,;]+', '', x)
	x = re.split("[,;]", x)
	return x


def mutant_type(name):
	if name is None:
		return 'rest'
	if name == 'wild type':
		return 'wildtype'
	elif ';' not in name:
		return 'single'
	elif name.count(';') == 1:
		return 'double'
	elif name.count(';') == 2:
		return 'triple'
	elif name.count(';') == 3:
		return 'quadruple'
	elif name.count(';') == 4:
		return 'quintuple'
	elif name.count(';') == 5:
		return 'sextuple'
	else:
		return 'rest'


def randomize_positions(list_mutants):
	new_list = []
	clusters = set([mutant[-1] for mutant in list_mutants])
	for cluster in clusters:
		# get a list with elements in that cluster
		small_list = [mutant for mutant in list_mutants if mutant[-1] == cluster]
		if len(small_list) > 3:
			ids, genes, lifespans, positions, clusts = zip(*small_list)
			list_positions = list(positions)
			random.shuffle(list_positions)
			small_list = list(zip(ids, genes, lifespans, list_positions, clusts))
		new_list += small_list
	return new_list


def rearrange_nodes(list_mutants, positions, val_limita, val_deplasare, bygenes, dist_between_genes):
	# la reteaua big nu trebuie sa tinem cont de genes pentru mutant2
	last_ls = 0
	last_pos = 0
	last_cl = 0
	cluster_max = [0]
	last_gene = ''
	max_x = 0
	min_x = 999999999

	for i in range(len(list_mutants)):
		mutant = list_mutants[i]
		id = mutant[0]
		gene = mutant[1]
		if gene == '-': gene = 'wild type'
		lifespan = mutant[2]
		x_position = positions[gene]
		if (float(lifespan) - last_ls) < val_limita and (not bygenes or gene == last_gene):
			x_position = last_pos + val_deplasare
			list_mutants[i].append(x_position)
			list_mutants[i].append(last_cl)
		else:
			list_mutants[i].append(x_position)
			list_mutants[i].append(last_cl + 1)
			last_cl += 1
			cluster_max.append(0)
		cluster_max[last_cl] = x_position
		last_ls = float(lifespan)
		last_pos = x_position
		last_gene = gene

	for mutant in list_mutants:
		if mutant[1] == '-': mutant[1] = 'wild type'
		m = cluster_max[mutant[-1]]
		# mutant[-2] = mutant[-2] + max_x[mutant[1]] / 2 - m / 2
		mutant[-2] = mutant[-2] + positions[mutant[1]] / 2 - m / 2
		if m - positions[mutant[1]] - dist_between_genes > 0:
			mutant[-2] = dist_between_genes * 0.9 * (mutant[-2] - positions[mutant[1]]) / (m - positions[mutant[1]]) + \
			             positions[mutant[1]]
		if mutant[-2] > max_x:
			max_x = mutant[-2]
		if mutant[-2] < min_x:
			min_x = mutant[-2] - 10
	# for i in range(len(response_data['genes'])):
	#     if response_data['genes'][i]['id1']==mutant[-5]:
	#         response_data['genes'][i]['x_position_1']=mutant[-2]

	list_mutants = randomize_positions(list_mutants)
	return_list = [max_x, list_mutants, min_x]

	return return_list
