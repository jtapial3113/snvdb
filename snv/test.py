# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
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

class AminoAcid(models.Model):
    one_letter_code = models.CharField(max_length=1L, primary_key=True)
    three_letter_code = models.CharField(max_length=3L)
    name = models.CharField(max_length=255L)
    class Meta:
        db_table = 'amino_acid'

class UniprotResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    uniprot_acc_number = models.CharField(max_length=6L)
    uniprot_position = models.IntegerField()
    amino_acid = models.CharField(max_length=1L)
    class Meta:
        db_table = 'uniprot_residue'

class Snv(models.Model):
    ft_id = models.CharField(max_length=10L, primary_key=True)
    type = models.CharField(max_length=20L)
    wt_aa = models.ForeignKey(Snv,related_name="+")
    mutant_aa = models.ForeignKey(Snv,related_name="+")
    uniprot = models.ForeignKey(Uniprot,db_column="uniprot_acc_number",related_name="snvs")
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

# AUTO
class Accessibility(models.Model):
    id = models.IntegerField(primary_key=True)
    interaction_id = models.IntegerField()
    chain_residue_id = models.IntegerField()
    bound_acc = models.CharField(max_length=10L)
    unbound_acc = models.CharField(max_length=10L)
    disulphide_bridge_no = models.IntegerField()
    class Meta:
        db_table = 'accessibility'


class Chain(models.Model):
    id = models.IntegerField(primary_key=True)
    pdb_id = models.CharField(max_length=4L, blank=True)
    pdb_chain = models.CharField(max_length=10L)
    pdb_model = models.IntegerField()
    seq_identity = models.CharField(max_length=10L)
    coverage = models.CharField(max_length=10L)
    seq_start = models.CharField(max_length=10L)
    seq_end = models.CharField(max_length=10L)
    uniprot = models.ForeignKey(Uniprot,db_column='uniprot_acc_number',related_name='chains')
    class Meta:
        db_table = 'chain'

class ChainResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    chain = models.ForeignKey('Chain',db_column='chain_id',related_name='residues')
    chain_position = models.CharField(max_length=10L)
    amino_acid = models.ForeignKey(AminoAcid,related_name="+")
    uniprot_residue = models.ManyToManyField(UniprotResidue,through=PositionMapping,related_name='chain_residues')
    class Meta:
        db_table = 'chain_residue'

class Interaction(models.Model):
    id = models.IntegerField(primary_key=True)
    chain_1 = models.ForeignKey(Chain,db_column='chain_1_id',related_name='+')
    chain_2 = models.IntegerField(Chain,db_column='chain_2_id',related_name='+')
    type = models.ForeignKey(InteractionType,related_name='+')
    filename = models.CharField(max_length=100L)
    class Meta:
        db_table = 'interaction'

class InteractionType(models.Model):
    type = models.CharField(max_length=20L, primary_key=True)
    class Meta:
        db_table = 'interaction_type'

class InterfaceResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    chain_residue = models.ForeignKey(ChainResidue,db_column='chain_residue_id',related_name='interface_residues')
    interaction = models.ForeignKey(Interaction,db_column='interaction_id',related_name='interface_residues')
    class Meta:
        db_table = 'interface_residue'

class PositionMapping(models.Model):
    id = models.IntegerField(primary_key=True)
    uniprot_residue_id = models.IntegerField()
    chain_residue_id = models.IntegerField()
    class Meta:
        db_table = 'position_mapping'

class SnvDisease(models.Model):
    id = models.IntegerField(primary_key=True)
    ft_id = models.CharField(max_length=10L)
    mim = models.IntegerField()
    class Meta:
        db_table = 'snv_disease'

class SnvType(models.Model):
    type = models.CharField(max_length=20L, primary_key=True)
    class Meta:
        db_table = 'snv_type'

class SnvUniprotResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    ft_id = models.CharField(max_length=10L)
    uniprot_residue_id = models.IntegerField()
    class Meta:
        db_table = 'snv_uniprot_residue'


