from __future__ import unicode_literals
from django.db import models
from django.core.urlresolvers import reverse


class Uniprot(models.Model):
	acc_number = models.CharField(max_length=6L, primary_key=True)
	sequence = models.TextField(blank=True)
	class Meta:
		db_table = 'uniprot'
    	
	def get_absolute_url(self):
		return reverse('uniprot-view', kwargs={'pk': self.acc_number})

class Snv(models.Model):
	ft_id = models.CharField(max_length=10L, primary_key=True)
	type = models.CharField(max_length=20L)
	wt_aa = models.CharField(max_length=1L)
	mutant_aa = models.CharField(max_length=1L)
	uniprot_acc_number = models.CharField(max_length=6L)
	uniprot_position = models.IntegerField()
	gene_code = models.CharField(max_length=10L, blank=True)
	db_snp = models.CharField(max_length=15L, blank=True)
	class Meta:
		db_table = 'snv'
	def get_absolute_url(self):
		return reverse('snv-view', kwargs={'pk': self.ft_id})

class Disease(models.Model):
	mim = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=255L, blank=True)
	class Meta:
		db_table = 'disease'
	def get_absolute_url(self):
		return reverse('disease-view', kwargs={'pk': self.mim})

'''

class Accessibility(models.Model):
	interaction_id = models.IntegerField()
	chain_id = models.IntegerField()
	chain_position = models.CharField(max_length=10L)
	bound_acc = models.CharField(max_length=10L)
	unbound_acc = models.CharField(max_length=10L)
	disulphide_bridge_no = models.IntegerField()
	class Meta:
		db_table = 'accessibility'

class AminoAcid(models.Model):
	one_letter_code = models.CharField(max_length=1L, primary_key=True)
	three_letter_code = models.CharField(max_length=3L)
	name = models.CharField(max_length=255L)
	class Meta:
		db_table = 'amino_acid'

class Chain(models.Model):
	id = models.IntegerField(primary_key=True)
	pdb_id = models.CharField(max_length=4L, blank=True)
	pdb_chain = models.CharField(max_length=10L)
	pdb_model = models.IntegerField()
	seq_identity = models.CharField(max_length=10L)
	coverage = models.CharField(max_length=10L)
	seq_start = models.CharField(max_length=10L)
	seq_end = models.CharField(max_length=10L)
	sequence = models.TextField()
	uniprot_acc_number = models.CharField(max_length=6L)
	class Meta:
		db_table = 'chain'

class ChainResidue(models.Model):
	chain_id = models.IntegerField()
	chain_position = models.CharField(max_length=10L)
	amino_acid = models.CharField(max_length=1L)
	class Meta:
		db_table = 'chain_residue'



class Interaction(models.Model):
	id = models.IntegerField(primary_key=True)
	chain_1_id = models.IntegerField()
	chain_2_id = models.IntegerField()
	type = models.CharField(max_length=20L)
	filename = models.CharField(max_length=100L)
	class Meta:
		db_table = 'interaction'

class InteractionType(models.Model):
	type = models.CharField(max_length=20L, primary_key=True)
	class Meta:
		db_table = 'interaction_type'

class InterfaceResidue(models.Model):
	chain_id = models.IntegerField()
	chain_position = models.CharField(max_length=10L)
	interaction_id = models.IntegerField()
	class Meta:
		db_table = 'interface_residue'

class PositionMapping(models.Model):
	uniprot_acc_number = models.CharField(max_length=6L)
	uniprot_position = models.IntegerField()
	chain_id = models.IntegerField()
	chain_position = models.CharField(max_length=10L)
	class Meta:
		db_table = 'position_mapping'


class SnvDisease(models.Model):
	ft_id = models.CharField(max_length=10L)
	mim = models.IntegerField()
	class Meta:
		db_table = 'snv_disease'

class SnvType(models.Model):
	type = models.CharField(max_length=20L, primary_key=True)
	class Meta:
		db_table = 'snv_type'

class UniprotResidue(models.Model):
	uniprot_acc_number = models.CharField(max_length=6L)
	uniprot_position = models.IntegerField()
	amino_acid = models.CharField(max_length=1L)
	class Meta:
		db_table = 'uniprot_residue'

'''
