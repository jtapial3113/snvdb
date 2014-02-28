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

from Bio import Entrez

##############################
##############################
##     GLOBAL METHOD
##############################
##############################

# get a list of SNVs and return appropriate color code to display
def get_color(snv_list):
	if len(snv_list)==1:
		if snv_list[0].type.type =='Disease':
			return  'red'
		elif snv_list[0].type.type =='Polymorphism':	
			return 'green'
		elif snv_list[0].type.type =='Unclassified':	
			return 'blue'
	return 'purple'			

###########################################################################
# Return SVG graphic code and Java Script (User need to add </svg> tag manually) 
###########################################################################
def create_svg_interaction(cu,_ischain1,i,header,height,classsuffix,interactid,maxlen,chain_reg,special):
	h_frame = str(25 + height)
	height = str(height)
	frame = 800
	color_code = [['#428bca','#285379'],['#5bc0de','#499AB2']] #darkblue / lightblue
	if not _ischain1:
		color_code = [['#5bc0de','#499AB2'],['#428bca','#285379']]
	if special:
		color_code = [['#5bc0de','#499AB2'],['#5bc0de','#499AB2']]
	classname_main = str(interactid)+'_'+cu[i].acc_number+classsuffix
	graphic_code = '<svg width= "850" height="'+h_frame+'">'+ header
	graphic_code += '<a xlink:href="'+cu[i].get_absolute_url()+'" target="_blank"><rect class = "'+classname_main+'"width="'+str(len(cu[i].sequence)*frame/maxlen)+'" height="'+height+'" x="5" y="25" rx="5" ry="5" style="fill:'+color_code[i][0]+';stroke-width:1;stroke:'+color_code[i][1]+'" /></a>'              
	java_code = '$(".'+classname_main+'").popover({content:"Uniprot ID: '+cu[i].acc_number+', '+str(len(cu[i].sequence))+' amino acids","placement": "bottom",trigger: "hover",container:"body"});'     
	for region in chain_reg:
		classname = str(i)+str(region[0])+str(region[1])+classsuffix
		content_data = ''
		if region[1]-region[0] == 1: #1residue case
			content_data = 'Residue '+str(region[0])
		else:
			content_data = 'Residue ' +str(region[0])+ ' to ' +str(region[1]-1)+ ' ('+str(region[1]-region[0])+' residues)'
		graphic_code +=  '<rect class ="'+classname+'" width="'+ str((region[1]-region[0])*frame/maxlen +1) +'" height="'+height+'" x="'+str((region[0])*frame/maxlen) +'" y="25" style="fill:#FF9933;" />'   			
			
		java_code+= '$(".'+classname+'").popover({content:"'+content_data+'","placement": "top",trigger: "hover",container:"body"});'
		
	return {'graphic_code':graphic_code,'java_code':java_code} 



##############################
##############################
##         CLASSES
##############################
############################## 
class Uniprot(models.Model):
	acc_number = models.CharField(max_length=6L, primary_key=True)
	sequence = models.TextField(blank=True)


	class Meta:
		db_table = 'uniprot'
		
	####################################################################
	# Return a list of all related snvs and their statistics
	####################################################################
	def get_Snv(self):	
		snvlist=[]
		for item in self.residues.all():					
			snvlist.extend(item.snvs.all())		
		di = po = un = 0.0		
		for item in snvlist:
			if item.type.type == 'Disease':
				di+=1
			elif item.type.type == 'Polymorphism':
				po+=1
			else:
				un+=1
		divider = float(len(snvlist))
		if divider==0:
			divider = 1
		stat1 = round(di*100/divider,1)
		stat2 = round(po*100/divider,1)
		stat3 = 100.0 - stat1 - stat2
		return [snvlist,[len(snvlist),"%.1f"%stat1,"%.1f"%stat2,"%.1f"%stat3]]

	def get_seq(self):
		mod_seq = ''
		for curr_pos in range(len(self.sequence)):
			if((curr_pos)%10 ==0):
				mod_seq = mod_seq + ' '			
			mod_seq = mod_seq+self.sequence[curr_pos]
		return mod_seq
	####################################################################
	# Return html code for SVG graphics and pdb alignment [ CHAIN ]
	####################################################################
	def get_graphic(self):
		outset = []
		for chain in self.chains.all():
			length = len(self.sequence)
			graphic_code = '<svg width="850" height="50">'
			graphic_code += '<rect width="800" height="12" x="0" y="10" rx="5" ry="5" style="fill:#428bca;stroke-width:1;stroke:#285379" />'                   
			graphic_code +=  '<text x="30" y="20" font-weight="bold" fill="white">'+self.acc_number+'</text> <text x="0" y="20" fill="white">|0</text><text x="200" y="20" fill="white">|'+str(length/4)+'</text><text x="400" y="20" fill="white">|'+str(length/2)+'</text><text x="600" y="20" fill="white">|'+str(length*3/4)+'</text><text x="800" y="20" fill="black">|'+str(length)+'</text>'
			graphic_code += '<rect width="'+ str(int(float(chain.coverage)*800/100)) +'" height="12" x="'+str(float(chain.seq_start)/float(length)*800)+'" y="25" rx="5" ry="5" style="fill:#5bc0de;stroke-width:1;stroke:#499AB2" />'   			
			graphic_code += '<text x="'+str(float(chain.seq_start)/float(length)*800+30)+'" y="35" font-weight="bold" fill="white"> PDB:'+chain.pdb_id+'</text><text x="'+str(float(chain.seq_start)/float(length)*800)+'" y="35" fill="white">|'+chain.seq_start+'</text><text x="'+str(float(chain.seq_end)/float(length)*800)+'" y="35" fill="black">|'+chain.seq_end+'</text>'
			graphic_code +='</svg>'

			#Alighment Method
			chain_res_set = list(chain.residues.all().extra(order_by = ['id']))
			res = None			
			mapping = None

			while chain_res_set: # pop until we find a residue that align within uniprot sequence			
				res = chain_res_set.pop(0)
				if res.uniprot_residue.all():
					mapping = res.uniprot_residue.all()[0].position
					break

			align_code = '<code style="background-color:#428bca ; color:white;">Seq 1:</code> '
			#Do each line for 50 letters
			cutoff = 50

			if res is not None:
				second_line=0
				for curr_pos in range(length):	
					if((curr_pos)%10 ==0):#First Line
						if(curr_pos!=0):
							align_code = align_code + ' '
					align_code = align_code+self.sequence[curr_pos]	

					if ((((curr_pos+1)%cutoff)==0 and curr_pos>0) or curr_pos==length-1 ): #Second line
						align_code+='<br><code style="background-color:#5bc0de ; color:white;">Seq 2:</code> '
						#do until second line position == first line position						
						while second_line <= curr_pos:
							if ((second_line%10==0) and (second_line > 0)):				
								align_code = align_code + ' '
							
							if(second_line == mapping-1): #shift in index, (position 1 = index 0 in python)
								color = 'yellow'
								if(res.amino_acid.one_letter_code != self.sequence[mapping-1]):
									color='#FF6600'
								align_code+= '<mark style="background-color:'+color+'">'+res.amino_acid.one_letter_code+'</mark>'

								while chain_res_set: # pop until we find a residue that align within uniprot sequence			
									res = chain_res_set.pop(0)
									if res.uniprot_residue.all():
										mapping = res.uniprot_residue.all()[0].position
										break
							else:
								align_code +='.'
												
							second_line+=1						
						if(second_line<length):
							align_code+='<br><code style="background-color:#428bca ; color:white;">Seq 1:</code> '
						
			outset.append({'obj':chain,'graphic':graphic_code,'alignent':align_code})	 	
		return outset

	###############################################
	# Returns reference_chain object
	################################################
	def get_ref_chain(self):
		for chain in self.chains.all():
			x = chain.superpositions_where_ref
			y = x.all()
			if len(y) > 0:
				return chain

	def get_color(self):
		if self.type.type =='Disease':
			return  set('red')
		elif self.type.type =='Polymorphism':	
			return 'green'
		elif self.type.type =='Unclassified':	
			return 'blue'
		return set('purple')	
	


	def interacting_partners(self):
		chains = self.chains.all()
		partners = []
		for chain in chains:
			p = chain.binding_partners()
			for partner in p:
				partners.append(partner.uniprot)
		# Return list of Uniprot objects
		return set(partners)
	


	###############################################
	# Returns Interaction Set with SVG graphic             [COMBINED WITH SNVS MAPPING]
	################################################
	def interactions(self):
		chains = self.chains.all()
		output = []
		interactionset = []
		header = '<text x="5" y="15" font-weight="bold" fill="black">'+self.acc_number+'</text>' 
		svgcode = create_svg_interaction([self,self],False,0,header,36,'mapped','0',len(self.sequence),[],True)
		interaction_reg_mark = [{'name':'default','info':'Default setting, No interaction marked','region':[],'id':'default','sequence':'','checked':'checked','graphic_code':svgcode['graphic_code'],'java_code':svgcode['java_code']}]
		outset = []
		#fetch and sort all related interactions
		for chain in chains:
			output =list(chain.interactions_1.all()) + list(chain.interactions_1.all())
			[outset.append(item) for item in output if item not in outset]  # eliminate redundancy
		outset = sorted(outset, key=lambda x: x.id) # sort the interactions by id

		#Process each interaction
		for interact in outset: 
			#get interface
			cu = [interact.chain_1.uniprot,interact.chain_2.uniprot] 
			chains_set=[[],[]]
			interact_res = [[],[]]

			_ischain1=False
			_isHomo = False
			if interact.chain_1.uniprot.acc_number == self.acc_number:
				_ischain1= True
			if interact.chain_1.uniprot.acc_number == interact.chain_2.uniprot.acc_number:
				_isHomo = True
			#Assign residues to either chain1 or chain2
			for item in interact.interface_residues.all():
				if item.chain_residue.chain_id == interact.chain_1.id:
					chains_set[0].append(item)
				else:
					chains_set[1].append(item)


			#post process for each chains
			chain_reg = [None,None] #Region markup for chain 1 and 2   
			res_pos = [[],[]] #Residue positions for chain 1 and 2

			for i in range(2):#do for chain1 & chain 2
				region = []
				if not chains_set[i]:#if no position found
					chain_reg[i] = []
					continue #skip

				starting = chains_set[i].pop(0)
				tmp = [int(starting.chain_residue.uniprot_residue.all()[0].position),int(starting.chain_residue.uniprot_residue.all()[0].position)+1]
				res_pos[i].append(int(starting.chain_residue.uniprot_residue.all()[0].position))
				for item in chains_set[i]:
					res_pos[i].append(item.chain_residue.uniprot_residue.all()[0].position)

					if int(item.chain_residue.uniprot_residue.all()[0].position) > tmp[1]:
						region.append(tmp)
						tmp = [int(item.chain_residue.uniprot_residue.all()[0].position),int(item.chain_residue.uniprot_residue.all()[0].position)+1]
					else:
						tmp[1] = int(item.chain_residue.uniprot_residue.all()[0].position)+1
				region.append(tmp)				
				chain_reg[i] = region
										
			#store marking region to Uniprot's local variable (to be used in SNVs mapping)
			if _isHomo: #Homo case, append both
				maxlen = len(cu[0].sequence)
				header = '<text x="5" y="15" font-weight="bold" fill="black">'+cu[0].acc_number+' interaction ID: '+str(interact.id)+'</text>' 
				svgcode = create_svg_interaction(cu,not _ischain1,0,header,36,'mapped',interact.id,maxlen,chain_reg[0],True)

				interaction_reg_mark.append({'name':str(interact.id)+'.1','info':'ID: '+str(interact.id)+', '+cu[0].acc_number+'-'+cu[1].acc_number,'region':res_pos[0],'id':'int'+str(interact.id)+cu[0].acc_number+'1','checked':'','graphic_code':svgcode['graphic_code'],'java_code':svgcode['java_code']})

				svgcode = create_svg_interaction(cu,not _ischain1,1,header,36,'mapped',interact.id,maxlen,chain_reg[1],True)
				interaction_reg_mark.append({'name':str(interact.id)+'.2','info':'ID: '+str(interact.id)+', '+cu[0].acc_number+'-'+cu[1].acc_number,'region':res_pos[1],'id':'int'+str(interact.id)+cu[1].acc_number+'2','checked':'','graphic_code':svgcode['graphic_code'],'java_code':svgcode['java_code']})
				
				
			elif _ischain1:
				maxlen = len(cu[0].sequence)
				header = '<text x="5" y="15" font-weight="bold" fill="black">'+cu[0].acc_number+' interaction ID: '+str(interact.id)+'</text>' 
				svgcode = create_svg_interaction(cu,not _ischain1,0,header,36,'mapped',interact.id,maxlen,chain_reg[0],False)
				interaction_reg_mark.append({'name':str(interact.id),'info':'ID: '+str(interact.id)+', '+cu[0].acc_number+'-'+cu[1].acc_number,'region':res_pos[0],'id':'int'+str(interact.id)+cu[0].acc_number,'checked':'','graphic_code':svgcode['graphic_code'],'java_code':svgcode['java_code']})
			else:
				maxlen = len(cu[1].sequence)
				header = '<text x="5" y="15" font-weight="bold" fill="black">'+cu[0].acc_number+' interaction ID: '+str(interact.id)+'</text>' 
				svgcode = create_svg_interaction(cu,not _ischain1,1,header,36,'mapped',interact.id,maxlen,chain_reg[1],False)
				interaction_reg_mark.append({'name':str(interact.id),'info':'ID: '+str(interact.id)+', '+cu[0].acc_number+'-'+cu[1].acc_number,'region':res_pos[1],'id':'int'+str(interact.id)+cu[1].acc_number,'checked':'','graphic_code':svgcode['graphic_code'],'java_code':svgcode['java_code']})




			#Create Graphic for each chain
			maxlen = max(len(cu[0].sequence),len(cu[1].sequence))
			graphic_code = ['','','',''] #1st[0] is for chain1, 2nd[1] is for chain2, 3rd[2] is for snv mapping, 4th[3] is for javacode to be combined with snvs

			for i in range(2):
				header = '<text x="5" y="15" font-weight="bold" fill="black">Partner '+str(i+1)+' : '+cu[i].acc_number+'</text>'
				svgcode = create_svg_interaction(cu,_ischain1,i,header,12,'',interact.id,maxlen,chain_reg[i],False)
				graphic_code[i] = svgcode['graphic_code']+'</svg><script>'+svgcode['java_code']+'</script>'
				
			interactionset.append({'obj':interact,'code':graphic_code})


	###################################################################
	# Returns html code for a sequence with mapped snvs 
	###################################################################

		seq=self.sequence
		mod_seq=''		
		snvlist=self.get_Snv()[0]
		mod = {}#a dict containing snvs and position
		for snv in snvlist:#get position of snvs into the dict
			if snv.uniprot_residue.position in mod:
				mod[snv.uniprot_residue.position].append(snv)
			else:
				mod[snv.uniprot_residue.position]=[snv]
	
		sorted_mod2 = sorted(mod.items(), key=lambda t: t[0]) #list of snv [pos0,pos1] pos0 = residue number, pos1 = snv obj 
		sorted_mod = []

		for option in interaction_reg_mark:#modified sequence for each interaction view
			#get region to be marked
			no_snv = False
			mark_reg = option['region']
			sorted_mod = list(sorted_mod2)
			if(sorted_mod):
				pos = sorted_mod.pop(0)
			else:
				no_snv = True	

			mod_seq=''		
			for curr_pos in range(len(seq)):
				interpos = False
				extraopt = ''
				textcol = 'black'
				letter = seq[curr_pos]
			
				if(curr_pos+1 in mark_reg):#mark interface site
					extraopt = 'text-decoration:underline overline;'
					textcol = '#FFCC00'
					letter = '<a href = "#" title = "Position '+str(curr_pos+1)+'" style="color:'+textcol+';'+extraopt+'">'+letter+'</a>'
					interpos = True

				if((curr_pos)%10 ==0):
					mod_seq = mod_seq + ' '	
				if(no_snv or curr_pos<pos[0]-1):#normal sequence
					mod_seq = mod_seq + letter
				else: #mark snvs
					
					 
					if not interpos: 
						textcol = 'white'
					pos_mute = ''			
					color = get_color(pos[1])
					frame = 800
					snvtype = pos[1][0].type.type
					if color == 'purple':
						snvtype = 'Multiple variations'
					option['graphic_code']+= '<rect class ="snv'+str(curr_pos+1)+'" width="'+ str(1*frame/len(seq) +1) +'" height="18" x="'+str((curr_pos+1)*frame/len(seq)) +'" y="25" style="fill:'+color+';" />' 
					option['java_code']+= '$(".snv'+str(curr_pos+1)+'").popover({content:"SNV position'+str(curr_pos+1)+', type: '+snvtype+'","placement": "top",trigger: "hover",container:"body"});'
					if color == 'purple':#multiple mutation case
						html = ''
						for item in pos[1]:					
							pos_mute=pos_mute + item.mutant_aa.one_letter_code +'('+item.type.type+') '	
							html = html+"<p><a href = '"+item.get_absolute_url()+"' target='_blank'>ID: "+item.ft_id+", Mutation: "+item.mutant_aa.one_letter_code +" ("+item.type.type+") </a></p>"
						mod_seq = mod_seq + '<mark style="background-color:'+color+'"><a href="#" style="color:'+textcol+';'+extraopt+'" class="open-AddBookDialog" data-id="'+html+'" data-toggle="modal" data-target=".bs-modal-sm"  title="Position '+str(curr_pos+1)+', Mutation: ' +pos_mute+'">'+seq[curr_pos]+'</a></mark>'	
					else:#One mutation case
						url = pos[1][0].get_absolute_url()
						pos_mute=pos_mute + pos[1][0].mutant_aa.one_letter_code +'('+pos[1][0].type.type+') '	
						mod_seq = mod_seq + '<mark style="background-color:'+color+'"><a href="'+url+'" target="_blank" style="color:'+textcol+';'+extraopt+'" title="Position '+str(curr_pos+1)+', Mutation: ' +pos_mute+'">'+seq[curr_pos]+'</a></mark>'	
						#add svg graphic
						
					if(len(sorted_mod)>0):
						pos = sorted_mod.pop(0)	
			
					else:
						no_snv = True

			option['sequence'] = mod_seq
			#print 'success'

		script = '<script type="text/javascript">$(document).ready(function(){ $(".default").show();$(\'input[type="radio"]\').click(function(){'
		for item in interaction_reg_mark:
			script += 'if($(this).attr("id")=="'+item['id']+'"){$(".box").hide();$(".'+item['id']+'").show();}'
		script+='});});</script>'	
	
		return [interactionset, mod_seq,interaction_reg_mark,script]
	###########################################################
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
    uniprot = models.ForeignKey(Uniprot,db_column='uniprot_acc_number',related_name="residues")
    position = models.IntegerField(db_column='uniprot_position')
    amino_acid = models.ForeignKey(AminoAcid,db_column='amino_acid',related_name="+")
    class Meta:
        db_table = 'uniprot_residue'

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

    def binding_partners(self):
        partners = []
        i1 = self.interactions_1.all()
        i2 = self.interactions_2.all()

        for interaction in i1:
            partners.append(interaction.chain_2)
        for interaction in i2:
            partners.append(interaction.chain_1)

        # Returns list of chains
        return(partners)



class InteractionType(models.Model):
    inter_type = models.CharField(db_column="type",max_length=20L, primary_key=True)
    class Meta:
        db_table = 'interaction_type'

class Interaction(models.Model):
    id = models.IntegerField(primary_key=True)
    chain_1 = models.ForeignKey(Chain,db_column='chain_1_id',related_name='interactions_1')
    chain_2 = models.ForeignKey(Chain,db_column='chain_2_id',related_name='interactions_2')
    inter_type = models.ForeignKey(InteractionType,db_column='type',related_name='+')
    filename = models.CharField(max_length=100L)
    class Meta:
        db_table = 'interaction'

    def get_snvs(self):
        cr_withsnv_partner1 = []
        for chain_residue in self.chain_1.residues.all():
            for ur in chain_residue.uniprot_residue.all():
                for snv in ur.snvs.all():
                    cr_withsnv_partner1.append(chain_residue)
        cr_withsnv_partner2 = []
        for chain_residue in self.chain_2.residues.all():
            for ur in chain_residue.uniprot_residue.all():
                for snv in ur.snvs.all():
                    cr_withsnv_partner2.append(chain_residue)

        return [set(cr_withsnv_partner1),set(cr_withsnv_partner2)]

    def get_pfam_mapping_positions(self):
    	#{chain_id:{mapping:[start_pdb_position,end_pdb_position]}}
    	chain1_mapping2positions = {}
    	chain2_mapping2positions = {}

    	for mapping in self.chain_1.uniprot.pfam_mappings.all():
			# Add to dictionary
			# Will fail with KeyError if that chain doesn't have a dictionary
			positions = mapping.get_pdb_positions(self.chain_1,self)
			if len(positions) == 2:
				chain1_mapping2positions[mapping] = positions
    	for mapping in self.chain_2.uniprot.pfam_mappings.all():
			# Add to dictionary
			# Will fail with KeyError if that chain doesn't have a dictionary
			positions = mapping.get_pdb_positions(self.chain_2,self)
			if len(positions) == 2:
				chain2_mapping2positions[mapping] = positions

    	return chain1_mapping2positions,chain2_mapping2positions



class ChainResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    chain = models.ForeignKey(Chain,db_column='chain_id',related_name='residues')
    position = models.CharField(max_length=10L,db_column='chain_position')
    amino_acid = models.ForeignKey(AminoAcid,related_name="+",db_column='amino_acid')
    uniprot_residue = models.ManyToManyField(UniprotResidue,through='PositionMapping',related_name='chain_residues')
    class Meta:
        db_table = 'chain_residue'

    def get_transformed_position(self,interaction):
    	
    	transform = PositionTransform.objects.get(chain=self.chain,interaction=interaction)

    	if transform.value != 0:
    		position = unicode(int(self.position) + transform.value)
    	else:
    		position = self.position

    	return position


class PositionMapping(models.Model):
    id = models.IntegerField(primary_key=True)
    uniprot_residue = models.ForeignKey(UniprotResidue,db_column='uniprot_residue_id',related_name='+')
    chain_residue = models.ForeignKey(ChainResidue,db_column='chain_residue_id',related_name='mapping')
    class Meta:
        db_table = 'position_mapping'

class Accessibility(models.Model):
    id = models.IntegerField(primary_key=True)
    interaction = models.ForeignKey(Interaction,db_column='interaction_id',related_name='+')
    chain_residue = models.ForeignKey(ChainResidue,db_column='chain_residue_id',related_name='accessibilities')
    bound_acc = models.CharField(max_length=10L)
    unbound_acc = models.CharField(max_length=10L)
    disulphide_bridge_no = models.IntegerField()
    class Meta:
        db_table = 'accessibility'

    def get_position(self):
    	cr = self.chain_residue
    	transform = PositionTransform.objects.get(chain=cr.chain,interaction=self.interaction)

    	if transform.value != 0:
    		position = unicode(int(cr.position) + transform.value)
    	else:
    		position = cr.position

    	return position


class InterfaceResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    chain_residue = models.ForeignKey(ChainResidue,db_column='chain_residue_id',related_name='interface_residues')
    interaction = models.ForeignKey(Interaction,db_column='interaction_id',related_name='interface_residues')
    class Meta:
        db_table = 'interface_residue'

    def get_position(self):
    	cr = self.chain_residue
    	transform = PositionTransform.objects.get(chain=cr.chain,interaction=self.interaction)

    	if transform.value != 0:
    		position = unicode(int(cr.position) + transform.value)
    	else:
    		position = cr.position

    	return position

class SnvType(models.Model):
    type = models.CharField(max_length=20L, primary_key=True)
    class Meta:
        db_table = 'snv_type'


class Snv(models.Model):
	ft_id = models.CharField(max_length=10L, primary_key=True)
	type = models.ForeignKey(SnvType,db_column='type',related_name='snvs')
	wt_aa = models.ForeignKey(AminoAcid,related_name="+",db_column="wt_aa")
	mutant_aa = models.ForeignKey(AminoAcid,related_name="+",db_column="mutant_aa")
	uniprot = models.CharField(max_length=6L,db_column="uniprot_acc_number")
	uniprot_residue = models.ForeignKey(UniprotResidue,db_column='uniprot_residue_id',related_name='snvs')
	#gene_code = models.CharField(max_length=10L, blank=True)
	db_snp = models.CharField(max_length=15L, blank=True)

	class Meta:
		db_table = 'snv'
	
	def get_marked_seq(self):
		uniobj = Uniprot.objects.filter(acc_number=self.uniprot) #get a list of object (it should return a list with one element inside)
		mod_seq = ''		
		if(len(uniobj)!=0): #if the object is available in our database
			pre_seq =  uniobj[0].sequence #get sequence data
			for curr_pos in range(len(pre_seq)): #run through all position
				if curr_pos%10 ==0:
					mod_seq = mod_seq + '  '
				if curr_pos==self.uniprot_residue.position-1:
					color = get_color([self])
					mod_seq =  mod_seq+'<mark style="background-color:'+color+'"><a style="color:white;" title="Position:'+str(self.uniprot_residue.position)+', Original Amino Acid:'+self.wt_aa.one_letter_code+' ">'+self.mutant_aa.one_letter_code+'</a></mark>'				 		
				else:				
					mod_seq = mod_seq + pre_seq[curr_pos]	
		return mod_seq

	def get_similar_snv(self):
		snvlist = list( set(self.uniprot_residue.snvs.all()) - set([self]))
		return snvlist
	
	def get_absolute_url(self):
		return reverse('snv-view', kwargs={'pk': self.ft_id})

	def get_genbank_id(self):
		handle = Entrez.esearch(db="gene", term="%s[Gene Name] AND homo sapiens[Organism]" % self.gene_code)
		record = Entrez.read(handle)
		gene_id = record["IdList"][0]
		return gene_id

class Disease(models.Model):
	mim = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=255L, blank=True)
	snvs = models.ManyToManyField(Snv,through='SnvDisease',related_name="diseases")

	class Meta:
		db_table = 'disease'

	def get_Snv(self):		#Return a list of related snvs and diseases

		snvlist=self.snvs.all()
		relatedsnv = []
		disease_sum = []
		relateduni = []
		for item in snvlist:				
			#find all diseases from all snvs that share the same uniprot_acc_number		
			related_snvs = Snv.objects.filter(uniprot=item.uniprot)
			related_disease = []			
			for	snv_item in related_snvs:
				for disease_item in snv_item.diseases.all():
					related_disease.append(disease_item)
					disease_sum.append(disease_item)
			related_disease_set = list(set(related_disease)-set(item.diseases.all()))
			if [item.uniprot,list(set(related_disease))] not in relateduni:
				relateduni.append([item.uniprot,list(set(related_disease))])
			relatedsnv.append({'obj':item, 'disease_set':related_disease_set})
		final_related_uniprot = relateduni
		final_disease_sum = list(set(disease_sum)-set([self]))
		return [relatedsnv,final_disease_sum,final_related_uniprot]


	def get_absolute_url(self):
		return reverse('disease-view', kwargs={'pk': self.mim})


class SnvDisease(models.Model):
    id = models.IntegerField(primary_key=True)
    snv = models.ForeignKey(Snv,db_column='ft_id')
    disease = models.ForeignKey(Disease,db_column='mim')
    class Meta:
        db_table = 'snv_disease'


class PfamHmm(models.Model):
    acc = models.CharField(max_length=12L, primary_key=True,db_column="hmm_acc")
    name = models.CharField(max_length=50L)
    type = models.CharField(max_length=50L)
    length = models.IntegerField()
    clan = models.CharField(max_length=50L)
    uniprots =  models.ManyToManyField(Uniprot,through='UniprotPfamMapping',related_name='pfam_hmms')
    class Meta:
        db_table = 'pfam_hmm'

class UniprotPfamMapping(models.Model):
    id = models.IntegerField(primary_key=True)
    uniprot = models.ForeignKey(Uniprot,db_column='uniprot_acc_number',related_name='pfam_mappings')
    hmm = models.ForeignKey(PfamHmm,db_column='hmm_acc')
    alignment_start_residue = models.ForeignKey(UniprotResidue,db_column='alignment_start_ur_id',related_name='+')
    alignment_end_residue = models.ForeignKey(UniprotResidue,db_column='alignment_end_ur_id',related_name='+')
    envelope_start_residue = models.ForeignKey(UniprotResidue,db_column='envelope_start_ur_id',related_name='+')
    envelope_end_residue = models.ForeignKey(UniprotResidue,db_column='envelope_end_ur_id',related_name='+')
    hmm_start = models.IntegerField()
    hmm_end = models.IntegerField()
    bit_score = models.DecimalField(max_digits=7, decimal_places=1)
    e_value = models.CharField(max_length=255L)
    significance = models.IntegerField()
    class Meta:
        db_table = 'uniprot_pfam_mapping'

    def get_pdb_positions(self,chain,interaction):
    	pdbpositions = []

    	for chain_residue in self.alignment_start_residue.chain_residues.all():
    		if chain_residue.chain == chain:
    			pdbpositions.append(chain_residue.get_transformed_position(interaction))
    	for chain_residue in self.alignment_end_residue.chain_residues.all():
    		if chain_residue.chain == chain:
    			pdbpositions.append(chain_residue.get_transformed_position(interaction))

    	if len(pdbpositions) == 2:
    		return pdbpositions
    	else:
    		return []

class ActiveSiteResidue(models.Model):
    id = models.IntegerField(primary_key=True)
    mapping = models.ForeignKey(UniprotPfamMapping,db_column='up_mapping_id',related_name="active_site_residues")
    residue = models.ForeignKey(UniprotResidue,db_column='active_site_ur_id',related_name='active_site_residues')
    class Meta:
        db_table = 'active_site_residue'

class SuperpositionMapping(models.Model):
    id = models.IntegerField(primary_key=True)
    ref_chain = models.ForeignKey(Chain,db_column='ref_chain_id',related_name='superpositions_where_ref')
    target_chain = models.ForeignKey(Chain,db_column='target_chain_id',related_name='superpositions_where_target')
    target_chain_letter = models.CharField(max_length=1L)
    class Meta:
        db_table = 'combined_uniprot_mapping'

class PositionTransform(models.Model):
    id = models.IntegerField(primary_key=True)
    interaction = models.ForeignKey(Interaction,db_column='interaction_id',related_name="transforms")
    chain = models.ForeignKey(Chain,db_column='chain_id',related_name="transforms")
    value = models.IntegerField()
    class Meta:
        db_table = 'position_transform'

















