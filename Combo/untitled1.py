#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 17:44:47 2021

@author: clairemoore-cantwell
"""



	def generate_candidates(self,root, suffix, observed):
		cand_list = []
		
		if root.kind != 'root':
			return("Error: The root is not valid!")
		if suffix.kind != 'suffix':
			return("Error: The suffix is not valid!")
		
		nonClist = ['ina','a','ga','i']
		
		cand_list = []
		NeedNoCcandidateStill = True
		ss = ''
		for s in suffix.allomorphs:
			if s[0] in nonClist: # allomorphs without a C
				# no thematic C
				obs = 1 if root.allomorphs[0][0][:-1]+s[0]==observed else 0
				cand_list.append(candidate(root.allomorphs[0][0][:-1]+s[0],[],obs,0.0,surfaceForm = root.allomorphs[0][0][:-1]+s[0]))
				
				# the (r) candidates
				for r in root.allomorphs:
					obs = 1 if r[0]+s[0]==observed else 0
					cand_list.append(candidate(r[0]+'(r)'+s[0],[],obs,r[1],surfaceForm =r[0]+s[0]))
					
			elif NeedNoCcandidateStill:
				# neither thematic C surfaces
				obs = 1 if root.allomorphs[0][0][:-1]+s[0][1:]==observed else 0
				cand_list.append(candidate(root.allomorphs[0][0][:-1]+s[0][1:],[],obs,0.0,surfaceForm =root.allomorphs[0][0][:-1]+s[0][1:]))
				ss=s[0][1:]
				NeedNoCcandidateStill = False
			
			else:
				# the (s) candidate
				obs = 1 if root.allomorphs[0][0][:-1]+s[0]==observed else 0
				cand_list.append(candidate(root.allomorphs[0][0][:-1]+'(s)'+s[0],[],obs,s[1],surfaceForm =root.allomorphs[0][0][:-1]+s[0]))
				
				# (rs) candidates
				for r in root.allomorphs:
					rtC = r[0][-1]
					sufC = s[0][0]
					if rtC == sufC:  # if applicable, the (rs) candidate
						obs = 1 if r[0]+s[0][1:]==observed else 0
						cand_list.append(candidate(r[0]+'(rs)'+s[0][1:],[],obs,r[1]+s[1],surfaceForm =r[0]+s[0][1:]))
						
		for r in root.allomorphs:
			# the (r) candidate
			obs = 1 if r[0]+ss==observed else 0
			cand_list.append(candidate(r[0]+'(r)'+ss,[],obs,r[1],surfaceForm =r[0]+ss))
						
				
		return cand_list










			if not suppressPFC:
				# Doesn't work right now - need to update how PFC's work
				for i in self.pfc:
					if i[1]>=700: # Impose a hard upper limit on PFC weights
						i[1]=700  # otherwise the calculation of probability, in particular probDenom, will fail
					cand.harmony += i[1]*(0 if cand.surfaceForm==i[0] else -1)
					# Assume always a single violation from each PFC for forms that don't match it
			try:
				self.probDenom += pow(math.e,cand.harmony)
			except OverflowError:
				print("Something's wrong with the exponentiation in calculating the MaxEnt denominator.  Check to make sure decay is working properly.  Python's patience with giant exponents only stretches so far...")
				print(self.inpt)
				print(cand)
				print(cand.harmony)
				print(w)
				print(self.pfc)     







		
		
		
		
		
		
		
def readOTSoft(file):
	"""Reads in an OTSoft file type"""
	print('reading tableaux...')
	tableaux = Tableaux()
	with open(file,"r") as f:
		lines=f.read().split('\n')
		# Check if the linebreak character is correct.  If it's not, the symptoms will be (a) only one line and (b) '\r' somewhere inside the line
		if bool(re.match('.*\r.*',lines[0])):
			if len(lines)==1:
				lines=lines[0].split('\r')
			else:
				print("EEK something is wrong with your linebreaks")

		lineno=0
		for line in lines:
			line=line.split('\t')
			#print line
			if lineno==0:
				firstLine = line
				#print firstLine
				if firstLine[1]=="":
					# OTSoft file? They have empty cells at the top
					pass
				if firstLine[0]=="input":
					# hgr file? They have the first three columns labeled
					inputType='hgr'
					#print inputType
					# Constraints are in the first line too, so grab those
					# Headers of these files:
					# input output (hidden) probability (tab.prob) Constraint1 Constraint2 ...
					offset = (3 if firstLine[2]=='hidden' else 2)
					hidden = (True if firstLine[2]=='hidden' else False)
					tokenFrequency = (True if firstLine[offset+1]=='tab.prob' else False)
					offset = offset + (2 if firstLine[offset+1]=='tab.prob' else 1)
					constraints=firstLine[offset:]
					#print offset
					#print tokenFrequency
					#print constraints
					tableaux.constraints = constraints
				else:
					print("I can't tell what type of file this is :(")

			elif inputType=='hgr':
				inpt = line[0]
				surfaceForm = (line[1] if hidden else None)
				c = (line[2] if hidden else line[1])
				observedProb = (line[3] if hidden else line[2])
				tokenProb = (line[offset-1] if tokenFrequency else 1)
				violations = line[offset:]
				#print(ur)
				if inpt not in tableaux.lexIDlist:
					#print 'add'
					tableaux.addLexEntry(LexEntry(inpt,tokenProb))
				for i in tableaux.lexList:
					if i.inpt==inpt:
						i.addCandidate(candidate(c,violations,observedProb,surfaceForm))
						break
			lineno+=1

	return tableaux









	def predictProbs(self,w):
		'''Convert harmony scores, and the MaxEnt denominator, to predicted probabilities for each candidate output in the Tableau '''
		self.calculateHarmony(w) # start by getting those harmonies
		self.probDenom = 0
		self.predProbsList=[]
		for cand in self.candidates:
			try:
				cand.predictedProb = pow(math.e,cand.harmony)/self.probDenom
			except OverflowError:
				print("Something's wrong with the exponentiation! Python's patience with giant exponents only stretches so far...")
				print(self.ur)
				print(cand.c)
				print(cand.harmony)
				print(w)
				print(self.pfc)
			except ZeroDivisionError:
				print("Somehow your MaxEnt denominator is zero!  Can't calculate probabilities this way")
				print(self.inpt)
				print(cand.c)
				print(cand.violations)
				print(cand.harmony)
				print(w)
				print(self.pfc)
				print(self.probDenom)

			self.predProbsList.append(cand.predictedProb)

	def getPredWinner(self):
		winCandidate = self.candidates[np.random.choice(range(0,len(self.candidates)),1,p=self.predProbsList)[0]]
		winner = winCandidate.surfaceForm
		return winner, winCandidate


	def getObsWinner_RIP(self,w):

		# create sub-tableau
		tab_rip = Tableau(self.inpt)
		#print("RIP")
		for c in self.candidates:
			if c.observedProb > 0.0:
				tab_rip.addCandidate(c)
		tab_rip.predictProbs(w)
		winner, winCandidate = tab_rip.getPredWinner()
		return winner, winCandidate

	def getObsWinner_sample(self):

		# Get candidate list
		# Get probability list
		winCandidate = self.candidates[np.random.choice(range(0,len(self.candidates)),1,p=self.obsProbsList)[0]]
		winner = winCandidate.c
		return winner, winCandidate

	def compareObsPred(self,w):
		self.predictProbs(w)
		pred, predCandidate=self.getPredWinner() # Sample from predicted distribution
		obs, obsCandidate=self.getObsWinner_RIP(w) # Via Robust Interpretive parsing
		for c in self.candidates:
			 if c.c==obs:
				 obsCandidate = c

		error = (0 if obs==pred else 1) 

		return error, obsCandidate, predCandidate
		




	def getObsWinner_RIP(self,w,):
		# create sub-tableau
		tab_rip = Tableau(self.inpt)
		for c in self.candidates:
			if c.observedProb > 0.0:
				tab_rip.addCandidate(c)
		tab_rip.predictProbs(w)
		winner, winCandidate = tab_rip.getPredWinner()
		return winner, winCandidate

	def getObsWinner_sample(self):
		''' only use when no hidden structure exists '''
		# Get candidate list
		# Get probability list
		winCandidate = self.candidates[np.random.choice(range(0,len(self.candidates)),1,p=self.obsProbsList)[0]]
		winner = winCandidate.c
		return winner, winCandidate




#		self.checkViolationsSign() # On initialization, make sure all violations are negative
#		self.activityLevel = activityLevel # float of activity level of thematic C of the candidate for calculating violations
	
#	def applyConstraints(self, constraints=Constraints.con):
#		self.violations=[i(self) for i in constraints]
		# TO DO: append, or overwrite?



class lexeme:
	def __init__(self, tag, segs = None, kind=None):
		self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
		self.segs = [] # Human-readable list of segments, corresponding to feature lookup tables, if using
		self.activitys = None # List of float value activity levels for self.segs.  Defaults to 1 for all segments if specified.  Optional
		self.linearSegOrder = [] # integers specifying the linear order of segs in self.segs
		# Example: t/z/n ami:
		# self.segs = ['t','z','n','a','m','i']
		# self.activitys = [.4, .5, .6, 1, 1, 1]
		# self.linearSegOrder = [1, 1, 1, 2, 3, 4]
		self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc. Optional
		self.freq = 0   #initialize at zero, increase during learning.  This number reflects the actual frequency of the lexeme during learning, rather than the frequency in the training data
		self.PFCs = None # list of PFC objects, optional.
		
	#def __str__(self):