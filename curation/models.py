# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Lags(models.Model):
	entrez_id = models.IntegerField(primary_key=True)
	tax_id = models.IntegerField()
	symbol = models.TextField()
	description = models.TextField(blank=True, null=True)
	wbid = models.TextField(blank=True, null=True)
	fbid = models.TextField(blank=True, null=True)
	mgiid = models.TextField(blank=True, null=True)
	locus = models.TextField(blank=True, null=True)
	type = models.TextField(blank=True, null=True)
	wbdescription = models.TextField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'lags'

	def __str__(self):
		return self.symbol


class Mutant(models.Model):
	id = models.IntegerField(primary_key=True)
	tax_id = models.IntegerField()
	name = models.TextField()
	genes = models.TextField(blank=True, null=True)
	temp = models.TextField(blank=True, null=True)
	lifespan = models.FloatField()
	pmid = models.IntegerField()
	effect = models.FloatField(blank=True, null=True)
	diet = models.TextField(blank=True, null=True)
	details = models.TextField(blank=True, null=True)
	comparison = models.TextField(blank=True, null=True)
	interaction_type = models.TextField(blank=True, null=True)
	strain = models.TextField(blank=True, null=True)

	class Meta:
		db_table = 'models'

	def __str__(self):
		return self.name


class ModelInteractions(models.Model):
	id1 = models.IntegerField(primary_key=True)
	id2 = models.IntegerField()
	comm = models.TextField(blank=True, null=True)

	class Meta:
		unique_together = (('id1', 'id2'),)


class NewArticle(models.Model):
	suggest_state = ((u'1', u'Approve'), (u'2', u'Reject'), (u'3', u'Maybe'),)
	id = models.AutoField(primary_key=True, editable=False)
	pmid = models.IntegerField(blank=True, null=True)
	email = models.EmailField(max_length=70)
	citation = models.CharField(blank=True, null=True, max_length=500)
	description = models.TextField(blank=True, null=True)
	state = models.CharField(max_length=1, choices=suggest_state, null=True)
	rejection_reason = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Approve(models.Model):
	id = models.AutoField(primary_key=True, editable=False)
	pmid = models.IntegerField()
	observation = models.TextField(help_text='Relevant comment for the article')
	model_id = models.IntegerField()
	number_mutations = models.IntegerField()
	model_name = models.CharField(max_length=100, help_text='Wild type or mutant')
	temperature = models.FloatField(help_text='°C', blank=True, null=True)
	diet = models.CharField(max_length=100, blank=True, null=True)
	lifespan = models.IntegerField(blank=True, null=True, help_text='Leave empty if is not available')


# new models
class Muutant(models.Model):
	# choices
	true_false_choices = ((1, 'Yes'), (2, 'No'))

	mutant_id = models.AutoField(primary_key=True)
	pmid = models.IntegerField()
	model_name = models.CharField(max_length=255)
	parent = models.CharField(max_length=255)
	entrez_id = models.IntegerField()
	intervention = models.CharField(max_length=255)
	temperature = models.CharField(max_length=255, blank=True, null=True)
	diet = models.CharField(max_length=255, blank=True, null=True)
	lifespan = models.FloatField()
	calorically_restricted = models.IntegerField(choices=true_false_choices)
	composite_id = models.CharField(max_length=255)

	def __str__(self):
		return str(self.pmid) + '|' + self.model_name


class CurationData(models.Model):
	pmid = models.IntegerField()
	observation = models.TextField(help_text='Relevant comment for the article')
	mutant = models.ManyToManyField(Muutant)

	def __str__(self):
		return str(self.pmid)


class PubmedData(models.Model):
	pmid = models.IntegerField()
	citation = models.CharField(max_length=255)
	abstract = models.TextField()

	def __str__(self):
		return str(self.pmid)


class KeggCel(models.Model):
	path_id = models.TextField(blank=True, null=True)
	path_name = models.TextField(blank=True, null=True)
	tax_id = models.IntegerField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'kegg_cel'


class KeggMappingCel(models.Model):
	path_id = models.TextField(blank=True, null=True)
	entrez_id = models.IntegerField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'kegg_mapping_cel'


class TissueExpression(models.Model):
	entrez_id = models.IntegerField(primary_key=True)
	tissue = models.TextField()
	our_name = models.TextField()

	class Meta:
		managed = False
		db_table = 'tissue_expression'
		unique_together = (('entrez_id', 'tissue'),)


class Edges(models.Model):
	page = models.ForeignKey(Mutant, models.DO_NOTHING, related_name='edge_page', blank=True, null=True)
	id1 = models.ForeignKey(Mutant, models.DO_NOTHING, related_name='edge_id1', db_column='id1', blank=True, null=True)
	id2 = models.ForeignKey(Mutant, models.DO_NOTHING, related_name='edge_id2', db_column='id2', blank=True, null=True)
	small_big = models.TextField()

	class Meta:
		managed = False
		db_table = 'edges'
		unique_together = (('page', 'id1', 'id2'),)


class Nodes(models.Model):
	page = models.ForeignKey(Mutant, models.DO_NOTHING, related_name='node_page', primary_key=True)
	node = models.ForeignKey(Mutant, models.DO_NOTHING, related_name='node_node')
	small_big = models.TextField()
	x_position = models.IntegerField()
	y_position = models.FloatField()

	class Meta:
		managed = False
		db_table = 'nodes'
		unique_together = (('page', 'node', 'small_big'),)


class GenePositions(models.Model):
	page = models.ForeignKey(Mutant, models.DO_NOTHING, blank=True, null=True)
	small_big = models.TextField(blank=True, null=True)
	genes = models.TextField(blank=True, null=True)
	x_position = models.FloatField(blank=True, null=True)

	class Meta:
		managed = False
		db_table = 'gene_positions'
