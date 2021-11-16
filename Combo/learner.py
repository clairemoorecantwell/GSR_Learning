#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np
from itertools import chain
import itertools
import re
from inspect import signature
import random



class Features:
	def __init__(self,filename,skipChar='x'):
		f = open(filename, "r")
		lines = f.readlines()
		self.featureNames = [i.strip() for i in lines[0].split('\t')[1:]]
		self.featureValues = {}
		self.skipChar = skipChar
		for i in lines[1:]:
			l = [j.strip() for j in i.split('\t')]
			self.featureValues[l[0]]=[val for val in l[1:]]
			# so this is now just numbers AND x's, all as str
			''' feature value skipChar is treated in this class as 'unspecified' and therefore matches with anything'''

		
	
	#TODO make a str() function
	
	def exists(self,featureList,add = False): # a list of tuples of (value,feature)
		'''Checks whether the list of feature values corresponds to a real segment in the feature set.  Returns the label of that feature set, or None if not found'''
		fs = [[str(i) for i,j in featureList if i!=self.skipChar],[str(j) for i,j in featureList if i!=self.skipChar]] 
		# This will be [[values],[features]], skipping over 'x' entries
		# skip over 'x' entries
		# create a new version of self.featureValues, pared down to just the features that appear in s
		indices = [self.featureNames.index(f) for f in fs[1]]
		newFeatureValues = [(i,[j[k] for k in indices]) for i,j in self.featureValues.items()]
		segID = [i for i,j in newFeatureValues if j == fs[0]]
		#print(segID) # List of all items corresponding to the given list of features
		if len(segID)==0:
			if add:
				print("Looks like you've provided a set of features that doesn't correspond to any segment:")
				print([i for i in zip(fs[0],fs[1])])
				choice = input("Would you like to add a segment for this set of features? (y/n)")
				while choice =='y':
					segToAdd = input("Please type the single character you would like to represent this set of features (or press enter to cancel): ")
					if segToAdd=='':
						choice == 'n'
					if choice =='y' and (segToAdd not in self.featureValues.keys()):
						newsegFeatureValues = ['x']*len(self.featureNames)
						for i in range(len(indices)):
							newsegFeatureValues[indices[i]] = fs[0][i]
						self.featureValues[segToAdd] = newsegFeatureValues
						print('Ok, added!')
						choice =='n'

					else:
						print("Sorry, ",segToAdd, " is already a phone in your feature set.  Please try another.")
			else:
				return None
		
		elif len(segID)>1:
			if add:
				print([i for i in zip(fs[0],fs[1])])
				print("This set of feature values corresponds to multiple segments.  Here they are:")
				print(segID)
				print("To manually choose one, just type the character for the segment you would like to use (or press enter to return None)")
				choice = input("Please type a choice: ")
				if choice in segID:
					return choice
				elif choice == '':
					return None
				else:
					print("Couldn't interpret your response.  exiting...")
					return None
			else:  #TODO think about this decision a little more.  Perhaps return the list of possible segments instead?
				return None
		elif len(segID) ==1:
			return segID[0]
		else:
			print("Yikes something has gone horribly wrong!")				
	
	def stringToF(self,string,seglabels = None):
		'''Convert a string to features '''
		'''returns a dictionary with each seg: [list of tuples of (value, feature)] '''
		'''also returns a list, with dictionary keys in order '''
		if seglabels: # Check that seglabels contains only unique values
			if len(seglabels) != len(set(seglabels)):
				seglabels = None
				print("Warning, seglabels contains non-unique values. stringToF() will now invent segment labels for your string.")
		segs = {}
		order = []
		for i in range(0,len(string)):
			if seglabels:
				k = seglabels[i]
			else:
				k = "seg"+str(i+1)
			segs[k]=[j for j in zip(self.featureValues[string[i]],self.featureNames)]
			order.append(k)
		
		return segs,order
	
	def featureToS(self,segs,order):
		'''converts a segment dictionary and an ordering to a string '''
		S = [] # in which to store the segments as we find them
		for s in order: # go through the segment labels in order
			S.append(self.exists(segs[s],add=True))
		return "".join([str(s) for s in S])
	




class candidate: 
	def __init__(self,c,violations,observedProb,surfaceForm=None): # removed: activitylevel
		self.c = c # the actual candidate 
		self.surfaceForm = surfaceForm if surfaceForm else c
		self.violations = violations # list of violations, in same order as constraints
		self.observedProb = observedProb # The observed probability of the candidate
		try: # make sure observedProb is a float, or can be converted to float
			self.observedProb = float(self.observedProb)
		except ValueError:
			print("It looks like candidate " + self.c + " has a probability that can't be converted to float.  Check if there's some text in that column of your spreadsheet")
		self.harmony = 0 # Not specified at initialization.	 This will be filled out in learning
		self.predictedProb = 0 # Again, to be filled out during learning.


class richCand(candidate):
	def __init__(self,c,violations,observedProb,segsDict,segsList,segsOrder=None,activitys=None,suprasegmentals = None,surfaceForm=None,operations=None):
		candidate.__init__(self,c,violations,observedProb,surfaceForm)
		self.segsDict = segsDict # This should be a dictionary with keys for segments, and values that are lists of tuples defining the features of each seg.
		# Example: {seg1: [(0, "front"),(1, "high"),(0,"back"),(0,"low")]}
		self.segsList = segsList # list of all segments
		self.segsOrder = segsOrder if segsOrder else [i for i in range(1,len(segsList)+1)]
		# set segsOrder to the order of the segments in segsList if a particular order is not specified
		#TODO think about if there is any circumstance in which this should NOT correspond to the linear order of segsList
		self.activitys = activitys if activitys else [1 for i in segsList] # set all activitys to 1 by default
		# These should/will only be non-1 values under Zimmerman-style GSRS (Z-GSRs)
		self.suprasegmentals = suprasegmentals
		self.operations =operations if operations else []
		
	def __repr__(self):
		return "richCand() object: '" + self.c + "'\n" + "attributes: segsDict, segsList, segsOrder, activitys, suprasegmentals, violations, harmony, predictedProb, observedProb, surfaceForm"
	
	def __str__(self):
		out = "Rich candidate '" + self.c + "'\n" + "Harmony: " + str(self.harmony)
		out += "\n" + "Predicted Probability: " + str(self.predictedProb)
		out += "\n" + "Violations: " + ' '.join([str(i) for i in self.violations])+'\n\n'
		maxLen = str(max([len(i) for i in self.segsList]))
		segform = ('{:^' + maxLen +'s} ')*len(self.segsList)
		out += segform.format(*self.segsList)
		out += '\n'
		out += segform.format(*[str(i) for i in self.activitys])
		out += '\n'
		out += segform.format(*[str(i) for i in self.segsOrder])
		out += '\n'
		out += '\n'.join([i+": "+' '.join([str(k) for k in j]) for i,j in self.segsDict.items()]) + '\n\n'
		out += 'Suprasegmentals:' + '\n' + '\n'.join([str(i) for i in self.suprasegmentals]) if self.suprasegmentals else 'No suprasegmentals'
		return out

	def __eq__(self,other):
		# check segs in order - segnames don't matter
		# check operations applied
		for i in range(0,len(self.segsList)):
			if self.segsDict[self.segsList[i]]!= other.segsDict[other.segsList[i]]:
				return 0
		self.operations.sort()
		other.operations.sort()
		if self.operations != other.operations:
			return 0
		
		return 1




def exampleCand():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg2 = [(1,"back"),(1,"high"),(0,"front"),(0,"low")]  # u
	seg3 = [(1,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg2":seg2,"seg3":seg3}
	order = ["seg1","seg3","seg2"]
	suprasegmentals = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return richCand('iau',[1,0,1],1,segs,order,suprasegmentals = suprasegmentals)

def exampleCand22():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg2 = [(1,"back"),(1,"high"),(0,"front"),(0,"low")]  # u
	seg3 = [(1,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg2":seg2,"seg3":seg3}
	order = ["seg1","seg2","seg3"]
	suprasegmentals = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return richCand('iau',[1,0,1],1,segs,order,suprasegmentals = suprasegmentals)

def exampleCandDup():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg2 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg3 = [(1,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg2":seg2,"seg3":seg3}
	order = ["seg1","seg2","seg3"]
	suprasegmentals = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return richCand('iau',[1,0,1],1,segs,order,suprasegmentals = suprasegmentals)

class Tableaux:
	def __init__(self,filename,noisy = False):
		self.tableaux = [] #list for tableaux to go into
		self.hidden = False
		self.tabProb = False
		self.constraintNames = []
		self.read(filename,noisy)
		
	def read(self,filename,noisy=True):
		print('reading in tableaux from file...')
		with open(filename,"r") as f:
			lines = f.readlines()
			
		# parse what kind of file this is
		line1 = lines.pop(0)
		line1 = line1.split('\t')
		line1 = [label.strip() for label in line1] # strip out leading and trailing whitespace for each entry in header row
		
		if line1[0] != 'input':
			print("WARNING: your first column is not labelled 'input' ... treating as input anyway")
		if line1[1] != 'candidate':
			print("WARNING: your second column is not labelled 'candidate' ... treating as candidate anyway")
		if line1[2] != 'obs.prob':
			if line1[2] != 'surface':
				try:
					float(lines[0].split('\t')[2])
					print("WARNING: your third column is not labelled either 'obs.prob' or 'surface' ... column can be treated as float, so I'm assuming it's supposed to be obs.prob")
				except ValueError:
					print("WARNING: your third column is not labelled either 'obs.prob' or 'surface' ... column cannot be treated as float, so I'm assuming it's supposed to be surface")
					self.hidden = True
					print("~~~~~~~~~~~ Hidden Structure is active ~~~~~~~~~~~~")
			else:
				print("Third column is labelled 'surface'")
				self.hidden = True
				print("~~~~~~~~~~~ Hidden Structure is active ~~~~~~~~~~~~")
				if line1[3] != 'obs.prob':
					try:
						float(lines[0].split('\t')[2])
						print("WARNING: your third column is labelled 'surface' but your fourth column is not labelled 'obs'prob' ... attempting to treat as obs.prob anyway")
					except ValueError:
						print("ERROR: your third columns is labelled 'surface' but your fourth column is not labeleld 'obs.prob', and cannot be converted to float.  Exiting...")
						return
		offset = 1 if self.hidden else 0
		if line1[3+offset] != 'tab.prob':
			print("No 'tab.prob' column ... assuming all tableaux should be equally probable")
		else:
			self.tabProb = True

		self.constraintNames = line1[4+offset:]
		
		# read in all the lines
		# create a new tableau when the input changes
		inpt = ''
		for line in lines:
			l = [entry.strip() for entry in line.split('\t')]
			p = l[3+offset] if self.tabProb else 1
			if l[0]!=inpt:  # if it's a new input - inputs have to be contiguous in the input file
				inpt = l[0]
				self.tableaux.append(Tableau(l[0],p))
				self.tableaux[-1].constraintNames = self.constraintNames
			
			s = l[2] if self.hidden else None
			self.tableaux[-1].addCandidate(candidate(l[1],[float(i) for i in l[4+offset:]],float(l[2+offset]),s))
			if p!= self.tableaux[-1].prob:
				print("WARNING: not all tab.prob entries for tableau "+ self.tableaux[-1].tag + " are equal.  ...using the first one.")
				# check if all tab.prob entries are the same for a given input - if not print a warning
				
		if noisy:
			for t in self.tableaux:
				print(t)
		
		wellFormed = True
		for t in self.tableaux:
			wellFormed = True if t.rect(userChoice = True) else False
		# Run tableau rectification on all tableau
		# Other checks
		
		return wellFormed  # return a bool for whether all tableaux are well formed or not
		

class Tableau: 
	def __init__(self,tag,prob=1,hiddenStructure=False):
		self.tag = tag # Human-readable tag to let the user know which tableau this is
		self.prob = prob
		self.candidates = [] # To be filled during tableau creation
		self.probDenom = 1 # denominator for calculating MaxEnt prob of each candidate
						   # this is the sum of each exponentiated harmony score
		self.predProbsList = [] # list of each candidate's predicted probability; used in sampling
								# gets filled (and updated) during learning
		self.obsProbsList = [] 	# list of each candidate's observed probability; used in sampling
		self.HList = [] # list of each candidate's harmony; for straight or Noisy HG
		self.winner = None
		self.constraintNames = None
		self.hiddenStructure = hiddenStructure
		self.surfaceCands = [] # a place to hold the unique surface candidates
		# Note: if hidden structure is active, then obsProbsList corresponds to surfaceCands.
		# Otherwise, it corresponds simply to candidates
		
	def __repr__(self):
		return "Tableau object '" + self.tag + "' with " + str(len(self.candidates)) + " candidates.  Winner: " + str(self.winner) + "\n" + "Attributes: tag, prob, candidates, probDenom, predProbsList, HList, obsProbsList, surfaceCands, hiddenStructure, constraintNames, winner"
	
	def __str__(self):
		vform = '{:4s} '   #format function for tableau - increase number for more space between cells
		longCand = max([len(i.c) for i in self.candidates])
		cform = '{:>'+str(longCand)+'s} '
		form = '{:3s} ' + cform + '{:5s} '*3 + vform*len(self.candidates[0].violations)
		out = "Tableau " + self.tag + "\n"
		# expect constraintNames to be a list of strings
		if self.constraintNames:
			vform = ''.join([('{:^' + str(len(i)) + 's} ') for i in self.constraintNames])
			form = '{:3s} ' + cform + '{:5s} '*3 + vform
			out += form.format(*[" "]*5 + [str(j) for j in self.constraintNames])
		for i in range(0, len(self.candidates)):
			w = " "
			if self.candidates[i-1].c == self.winner:
				w = " --> "
			v = self.candidates[i-1].violations
			row = [w] + [self.candidates[i-1].c,self.candidates[i-1].observedProb,self.predProbsList[i-1],self.HList[i-1]] + v
			out += '\n' + form.format(*[str(j) for j in row])
		return out


	def addCandidate(self,cand):
		self.candidates.append(cand)
		if cand.surfaceForm != cand.c:
			self.hiddenStructure = True
		if cand.surfaceForm not in self.surfaceCands:
			self.surfaceCands.append(cand.surfaceForm)
			self.obsProbsList.append(cand.observedProb)
		# Add placeholders for the others so the tableau is always printable
		self.predProbsList.append("EMPTY")
		self.HList.append("EMPTY")


	def checkViolationLength(self): 
		'''check if all the violation vectors are the same length'''
		c1 = self.candidates[0]
		l = len(c1.violations)
		for i in self.candidates:
			if len(i.violations) != l:
				print("Not all violation vectors are the same length!\n", "Candidate ",i.c, "has ", len(i.violations), ", while candidate",c1.c, "has ", l, " violations.")
				return 0
			else:
				return 1
			
	def checkViolationsSign(self,convert = True, userChoice = False):
		'''check if all violations in the tableau are positive.  In this program, we are assuming positive violations, (mostly) positive weights, and the negative sign is added with the harmony calculation'''
		allNegative = True # if all violations are negative, convert all to positive
		allPositive = True # these can't both be true of course ... unless all violations are zero
		for i in self.candidates:
			if min(i.violations)<0:
				allPositive = False
			if max(i.violations)>0:
				allNegative = False
		
		if allPositive:
			if allNegative:
				print("WARNING: your constraint violations are all zero! Proceeding anyway...")
			return 1
		elif allNegative:
			print("WARNING: your constraint violations are all negative numbers.  For the learner to function normally, they probably need to be converted to positive")
			if userChoice:
				proceed = input("Proceed? (y/n)")
				if proceed.lower()=='n':
					convert = False
			if convert:
				for i in self.candidates:
					i.violations = [-v for v in i.violations]
				if self.checkViolationsSign():
					print("Negative violations successfully converted")
					return 1
		else:
			print("WARNING: Your constraint violations are a mix of positive and negative numbers.  Proceed with caution!")
			return 0


	def rect(self,userChoice = False):
		l = self.checkViolationLength()
		s = self.checkViolationsSign(userChoice)
		#what else?
		return bool(l and s)

			
	def calculateHarmony(self, w): 
		'''Takes a vector of weights, equal in length to the violation vectors of the candidates.  Populates the harmony parameter of each candidate based on the weight vector w'''
		# note that w could be made up of a variety of constraint types, markedness and PFC's for example.
		self.HList = []
		for cand in self.candidates:
			# Calculate that good 'ole dot product!
			cand.harmony = -sum(viol*weight for viol,weight in zip(cand.violations,w))
			# harmony will be a negative number if all constraint weights are positive.
			# May become positive when constraint weights go negative
			self.HList.append(cand.harmony)


	def predictProbsMaxEnt(self,w):
		'''Convert harmony scores, and the MaxEnt denominator, to predicted probabilities for each candidate output in the Tableau '''
		self.calculateHarmony(w) # start by getting those harmonies
		self.probDenom = sum([pow(math.e,cand.harmony) for cand in self.candidates])
		self.predProbsList=[]
		for cand in self.candidates:
			try:
				cand.predictedProb = pow(math.e,cand.harmony)/self.probDenom
			except OverflowError:
				print("Something's wrong with the exponentiation! Python's patience with giant exponents only stretches so far...")

			except ZeroDivisionError:
				print("Somehow your MaxEnt denominator is zero!  Can't calculate probabilities this way")
			self.predProbsList.append(cand.predictedProb)
		
	
	def getPredWinner(self,w=None,theory = 'MaxEnt'):
		''' generates a predicted winner based on weights and theory'''
		# TODO add stochastic OT functionality here
		if theory == 'HG' or theory == 'NoisyHG':
			# if Noisy HG, here's where to add the noise probably
			if w:
				self.calculateHarmony(w)
			bestH = max(self.HList)
			bestCands = [cand for cand in self.candidates if cand.harmony == bestH]
			winCandidate = np.random.choice(bestCands,1)[0] # if there's more than one optimal candidate according to the harmony, select one at random.
		elif theory =='MaxEnt':
			if w:
				self.predictProbsMaxEnt(w)
			winCandidate = self.candidates[np.random.choice(range(0,len(self.candidates)),1,p=self.predProbsList)[0]]
		else:
			print("Unrecognized theory type " + theory + ".  Acceptable types are 'HG', 'NoisyHG', and 'MaxEnt'.")
			return None
		
		return winCandidate


	def getObsCandidate(self,w=None,theory='MaxEnt'):
		''' find the observed candidate to use for learning update '''
		''' If multiple candidates match a single output, use EIP from jaroscz 2013 to choose a parse/hidden structure/predicted candidate '''
		obsOutput = self.getObsOutput()
		matchCands = [] #holding all candidates whose surface form matches the observed output
		for cand in self.candidates:
			if obsOutput == cand.surfaceForm:
				matchCands.append(cand)
		if len(matchCands)>1: # if more than one candidate matched the observed output, there is hidden structure to parse
			#try to parse hidden structure in a way that is theory agnostic, or at least passes theory on to the internal function calls....
			# generate a sub-tableau with just matchCands, but weights = w
			subTab = Tableau(obsOutput,hiddenStructure=False)
			for cand in matchCands:
				subTab.addCandidate(cand)
			winCandidate = subTab.getPredWinner(w,theory)
		else:
			winCandidate = matchCands[0].c, matchCands[0]
			
		return winCandidate
	
	def getObsOutput(self):
		''' simple function to get the observed output from the obsProbsList'''
		obsOutput = self.surfaceCands[np.random.choice(range(0,len(self.surfaceCands)),1,p=self.obsProbsList)[0]]
		return obsOutput


	def compareObsPred(self,w,theory='MaxEnt'):
		predCandidate=self.getPredWinner(w,theory)
		obsCandidate=self.getObsCandidate(w,theory) 
#		for c in self.candidates:
#			 if c.c==obs:
#				 obsCandidate = c
# ^^ why is this here?  Is it necessary for something?

		error = (0 if obsCandidate.surfaceForm==predCandidate.surfaceForm else 1) 

		return error, obsCandidate, predCandidate
		

class Grammar:
	def __init__(self,filename,constraints,operations,featureSet):
		self.trainingData = trainingData(filename)  # An array or something containing the learning data
		self.featureSet = featureSet
		self.constraints = constraints
		self.operations = operations # Read these off the top of the input data file.
		self.w = [] # Weights, starts empty
		self.initializeWeights() # Initialize weights when Tableaux object is created (to zero, or some other vector depending on how you call this function.)
		self.t = 0	# For learning, t starts at 0
		self.learningRate = 0.1
		self.activityUpdateRate = 0.05
		self.PFC_startW = 10
		self.PFC_decay = 0.0001
	
	
	def createLearningPlaylist(self,n):
		# n is total number of learning simulations
		return [self.trainingData.learnData[i] for i in list(np.random.choice(range(0,len(self.trainingData.learnData)),n,p=self.trainingData.sampler))]



	def initializeWeights(self,w=None):
		'''Function to initialize the weights - can take an argument, which is hopefully the same length as the number of constraints in the Tableaux object.  If it doesn't get that argument, it will initialize them to zero. '''
		# TODO (low priority atm) Add functionality to initialize weights to random values
		if w is None:
			self.w = [0]*len(self.constraints)
		else:
			if len(w)==len(self.constraints):
				self.w=w
			else:
				print("WARNING: you tried to initialize weights with a list that's not the same length as your list of constraints.	 This probably didn't work so well.")
				# This will print a warning, but it won't actually stop you from initializing constraints badly?  Maybe this is a problem that should be fixed.
   
	def calculate_sample_weights(self,frequencies):
	
		#helper function; calculates weights for the weighted sample
		#takes a list of word frequencies as input 
		#returns a set of weights 
		
		total = sum(frequencies)
		weights = [ round(freq / total, 10) for freq in frequencies] 
		return weights
			

#######################
		# Need to start with creating the playlist
		#And, add a observed output arg to the tableau creation
	def update(self,datum): # datum is an entry from playlist
		# Start with a learning datum
		# Create a tableau
		tab = createTableau(datum[0], self.constraints, self.operations, self.featureSet,datum[1])

		e, obs, pred = tab.compareObsPred(self.w)

		print(e,obs.c,pred.c,obs.violations,pred.violations,obs.harmony,obs.predictedProb,pred.harmony,pred.predictedProb)
		if e:
			#update general weight: perceptron update
			self.w = [wt-(p-o)*self.learningRate for wt,p,o in zip(self.w,pred.violations,obs.violations) ]
			#self.w = [0 if w<0]
			
			#update activity levels of correct thematic C, if any
			# First, boost activity levels on thematic C's if an (r), (s), or (rs) candidate was observed (regardless of predicted candidate)
			if re.search('\(r',obs.c): #if (r) or (rs) is the observed form)
				C = re.search("(.)(\(r)",obs.c).group(1) # grab out the thematic C
				for a in datum[1].allomorphs: # Find the thematic C in the allomorphs of the root that we are learning with
					if a[0][-1]==C: 
						a[1]+=self.activityUpdateRate
						
			if re.search('s\)',obs.c): #if (s) or (rs) is the observed form
				C = re.search("(s\))(.)",obs.c).group(2) # grab out the thematic C
				for a in datum[2].allomorphs: # Find the thematic C in the allomorphs of the root that we are learning with
					if a[0][0]==C: 
						a[1]+=self.activityUpdateRate
						
			# Next, decrease activity rate if pred form has a thematic C and obs. did not
			if not re.search('\(',obs.c) and re.search('\(r',pred.c):
				C = re.search("(.)(\(r)",pred.c).group(1) # grab out the thematic C
				for a in datum[1].allomorphs: # Find the thematic C in the allomorphs of the root that we are learning with
					if a[0][-1]==C: 
						a[1]-=self.activityUpdateRate
						a[1] = 0.0 if a[1]<0.0 else a[1] #bottom out activity levels at zero
			
			if not re.search('\(',obs.c) and re.search('s\)',pred.c):
				C = re.search("(s\))(.)",pred.c).group(2) # grab out the thematic C
				for a in datum[2].allomorphs: # Find the thematic C in the allomorphs of the root that we are learning with
					if a[0][0]==C: 
						a[1]-=self.activityUpdateRate
						a[1] = 0.0 if a[1]<0.0 else a[1] #bottom out activity levels at zero
		self.t+=1
		print(self.w) 
		return e
		
	
	def epoch(self,playlist,niter,start=0):
		errors = 0
		for i in range(0,niter):
			errors+=self.update(playlist[start+i])
			print(start+i)
			
		error_rate = errors/niter
		# print out list of weights
		# print out SSE
		return error_rate
		
		
		
	def learn(self,nIterations,nEpochs):
		
		playlist = self.createLearningPlaylist(nIterations*nEpochs)
		for i in range(0,nEpochs):
			rate = self.epoch(playlist,nIterations,start=nIterations*i)
			print(rate)

	

	
class lexeme:
	def __init__(self, tag, segmentList = None, kind=None):
		self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
		self.segmentList = segmentList if segmentList else [i for i in tag]  # Human-readable list of segments, corresponding to feature lookup tables, if using
		self.segLabels = [self.segmentList[0]]+[self.segmentList[i] if self.segmentList[i] not in self.segmentList[:i-1] else self.segmentList[i]+str(i) for i in range(1,len(self.segmentList))] #create list of unique segment labels, to be used in candidate generation and evaluation by PFCs
		self.activitys = [1 for i in self.segmentList] # List of float value activity levels for self.segs.  Defaults to 1 for all
		self.linearSegOrder = [i for i in range(1,len(self.segmentList)+1)] # integers specifying the linear order of segs in self.segs. starts at 1
		# Example: t/z/n ami:
		# self.segs = ['t','z','n','a','m','i']
		# self.activitys = [.4, .5, .6, 1, 1, 1]
		# self.linearSegOrder = [1, 1, 1, 2, 3, 4]
		self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc. Optional
		self.freq = 0   #initialize at zero, increase during learning.  This number reflects the actual frequency of the lexeme during learning, rather than the frequency in the training data
		self.PFCs = None # list of PFC objects, optional.
		
	def __str__(self):
		out = 'Lexeme ' + str(self.tag) +' (' + str(self.kind) + ', f:' + str(self.freq) + ' )\n'
		segform = '{:2s} '*len(self.segmentList)
		out += segform.format(*self.segmentList)
		out += '\n'
		out += segform.format(*[str(i) for i in self.activitys])
		out += '\n'
		out += segform.format(*[str(i) for i in self.linearSegOrder])
		out += '\n'
		out += [print(i)+'\n' for i in self.PFCs] if self.PFCs else 'No PFCs'
		return out	
	
	def toRichCand(self,featureSet):
		''' produces the faithful candidate for just this one lexeme, given a Feature object, featureSet '''
		#TODO first check that all segments are even in featureSet
		
		#Now, get the segments in all possible orders
		segsInOrder = []
		segLabelsInOrder = []
		for i in range(1,max(self.linearSegOrder)+1):
			indices = [index for index,value in enumerate(self.linearSegOrder) if value ==i]
			print(indices)
			if len(indices)>0:
				segsInOrder.append([self.segmentList[i] for i in indices])
				segLabelsInOrder.append([self.segLabels[i] for i in indices])
		cands = list(itertools.product(*segLabelsInOrder))
		print(cands)
		# violations: empty
		# observedProb: empty
		
		rcs = []
		for c in cands:
			#create string with numbers stripped
			strRep = ''.join([re.sub('[0-9]','',s) for s in c])
			segsDict, segsList = featureSet.stringToF(strRep,list(c))
			a = [self.activitys[self.segLabels.index(i)] for i  in c ]
			rcs.append(richCand(''.join(c),[],0,segsDict,segsList,activitys=a))		
		return rcs

class Lexicon:
	
	def __init__(self,filename=None,sheetNo=1):
		self.lexemeList = {}  # dict will have the structure {tag: lexeme}
		self.freqList = []    #empty list for storing each lexeme's frequency - used for sampling
		if filename is not None:
			self.read_input(filename,sheetNo)
		
	def add_lexeme(self,l):
		# Add a lexeme to the lexemeList
		self.lexemeList[l.tag]=l
		self.freqList.append(l.freq)
		
	
	def update_freqList(self):
		# update freqList with all lexemes' frequencies, in case they have changed
		self.freqList = []
		for l in self.lexemeList:
			self.freqList.append(l.freq)
			
	def read_input(self,file_name, sheet_number):  # sheet_number starts from 1
		# TODO add functionality to check if its an excel file or .txt; and then also be able to read .txt
		# TODO further, add try... except to check for proper loading of pandas, and if not, throw up a useful error
		#reading excel into dataframe
		input_dt_frame = read_excel(file_name, sheet_number-1 ) #this is for the sheet#1; 
			#dataframe into np array
		input_np = input_dt_frame.to_numpy()
		
		cpyarr = input_np.tolist()
		roots = []  # |
		suffix = []
		suffix_helper = []# |
		them_c_helper = []
		them_c = []
		allomorphs = []
		
		# thematic c =(['t','n','f','g','m','l','s','q']) Note of list of all the thematic C's
		for x in range (len(cpyarr)):  # looping through Julia's numpy array and separating roots, suffix, and them_c columns
			roots.append(cpyarr[x][6])
			suffix_helper.append(cpyarr[x][3])
			them_c_helper.append(cpyarr[x][2])
	
		suffix = list(set(suffix_helper))
		them_c = list(set(them_c_helper))
		them_c = list(filter(lambda x: str(x)!= 'nan',them_c))  # to not generate something like "tagiNA"

		for x in range(len(roots)):  # looping through roots column
			allomorphs = []
			for y in them_c:  # concat each root with all possible them_c
				allomorphs.append([roots[x]+y]+[0])
			self.add_lexeme(lexeme(roots[x], allomorphs, 'root'))

		tag = 'ina'
		allomorphs = [['ina',0],['a',0]]
		for y in them_c:
			allomorphs.append([y+'ia']+[0])
		self.add_lexeme(lexeme(tag,allomorphs,'suffix'))
		
		tag = 'aga'
		allomorphs = [['ga',0]]
		for y in them_c:
			allomorphs.append([y+'aga']+[0])
		self.add_lexeme(lexeme(tag,allomorphs,'suffix'))
			
		tag = 'aqi'
		allomorphs = []
		for y in them_c:
			allomorphs.append([y+'aqi']+[0])
		self.add_lexeme(lexeme(tag,allomorphs,'suffix'))

		tag = 'i'
		allomorphs = []
		for y in them_c:
			allomorphs.append([y+'i']+[0])
		self.add_lexeme(lexeme(tag,allomorphs,'suffix'))
		
		tag = 'zero'
		allomorphs=['']
		self.add_lexeme(lexeme(tag,allomorphs,'suffix'))
		

def exlex_joli():
	#joli    A simple adjective with nothing fancy
	return lexeme('joli',kind='Adj')

def exlex_petit():
	#petit    An adjective with partial activation on the final t
	p = lexeme('petit',kind='Adj')
	p.activitys = [1,1,1,1,0.4]
	p.PFCs = [PFC(10,('1','voice'),'e'),PFC(10,('1','labial'),'p'),PFC(10,('1','coronal'),'t4')]
	return p

def exlex_ami():
	#ami    Noun with three competing segments in first position
	a = lexeme('ami',segmentList = ['t','z','n','a','m','i'],kind='Noun')
	a.linearSegOrder = [1,1,1,2,3,4]
	a.activitys = [0.6,0.6,0.6,1,1,1]
	a.PFCs = [PFC(10,('1','nasal'),'n'),PFC(10,('0','voice'),'t'),PFC(10,('1','low'),'a')]
	return a

def exlex_hero():
	#hero    A noun that lacks and liason consonants in its lexical representation
	return lexeme('ero',kind='Noun')



class PFC: #Contains function(s) for calculating a PFC's violations
	def __init__(self,w,feature=None,seg=None,seg2=None,typ='feature_on_segment'):
		self.w = w
		self.feature = feature # must be a tuple (0, 'high'), (1, 'coronal') etc.
		self.seg = seg  # name of a seg in the lexeme that this PFC belongs to
		self.seg2 = seg2 # note that seg names must be immutable in the lexeme!
		self.typ = typ
		
		# auto-calculate PFC type
		# note that type 'suprasegmental' must be defined by the function call, and cannot be specified within (it can't be distinguished in form from exists_feature)
		if feature is None and seg is not None and seg2 is not None:
			self.typ = 'prec'
			self.name = seg+'<<'+seg2
			
		if feature is not None and seg is None and seg2 is None and typ!='suprasegmental':
			self.typ = 'exists_feature'
			self.name = str(feature)
		
		self.name = seg+":"+str(feature)
		
	def evaluate(self,cand): #evaluates a richCand object
		if self.typ=='feature_on_segment':
			viol = 0 if self.feature in cand.segsDict.get(self.seg,[]) else 1
		elif self.typ=='exists_feature':
			viol = 0 if self.feature in [i for i in chain(*cand.segsDict.values())] else 1
		elif self.typ =='prec':
			#order of seg1 is segsOrder[segsList.index(seg1)]
			if self.seg in cand.segsList and self.seg2 in cand.segsList:
				viol = 0 if cand.segsOrder[cand.segsList.index(self.seg)] < cand.segsOrder[cand.segsList.index(self.seg2)] else 1
			else:
				viol = 1
		elif self.typ == 'suprasegmental':
			viol = 0 if self.feature in cand.suprasegmentals else 1
		else:
			print("Error!  You've passed the PFC something that's not a valid type.  Types are 'feature_on_segment', 'prec', 'exists_feature', 'suprasegmental'")
		return viol
	
#TODO more thorough testing of PFC functionality

class trainingData:
	'''essentially, a list of lexeme sets paired with correct surface forms, and frequencies '''
	def __init__(self,filename):
		self.lexicon = [] # a list of lexemes
		self.lexTags = []
		self.learnData = []
		self.sampler = []
		f = open(filename, "r")
		lines = f.readlines()
		if lines[0].split('\t')[1]=='lexeme':
			specialLex = True
		for i in lines[1:]:
			l = [j.strip() for j in i.split('\t')]
			lex = l[0].split("_")
			if specialLex:
				spLex = l[1].split("_")
			else:
				splex = lex
			lexList = []
			for item,sp in lex,spLex:
				if item not in self.lexTags:
					if specialLex:
						self.lexicon.append(lexeme(item,[ch for ch in sp]))
					else:
						self.lexicon.append(lexeme(item))
					self.lexTags.append(item)
				lexList.append(self.lexicon[self.lexTags.index(item)])
			self.learnData.append([lexList,l[1]])
			self.sampler.append(float(l[3]))
		self.sampler = [s/sum(self.sampler) for s in self.sampler] # convert to a well-formed distribution

	

#class Grammar(constraints, operations, trainingData, featureSet, w=None, EVAL='MaxEnt', theory='RST'):
	
	

def createTableau(lexemes,constraints,operations,featureSet,obsOutput,w = None,scramble=False):
	'''create a tableau from lexemes, constraints, operations'''
	# lexemes is an ordered list of lexemes, or a single lexeme
	# TODO expand to more than two lexemes
	# TODO separate out markedness and faithfulness
	# constraints, operations, are lists of functions.  see constraints.py for details
	if not w:
		w = [0 for c in constraints]
	constraintList = [c.name for c in constraints]

	if not scramble:
		individualCands = []
		for l in lexemes:
			individualCands.append(l.toRichCand(featureSet))
		faiths = list(itertools.product(individualCands[0],individualCands[1]))
		# This is where it's limited to two lexemes only
	
	#TODO implement scramble option
		
	# concatenate richCands
	fcs = [] #'fc' = 'faithful candidate'
	for fc in faiths:
		#begin creating the new richCand
		newSegsList = fc[0].segsList[:]
		newSegsDict = fc[0].segsDict.copy()
		newActivitys = fc[0].activitys[:]
		newSuprasegmentals = fc[0].suprasegmentals[:] if fc[0].suprasegmentals else []
		for i in range(1,len(fc)): # go through morphemes
			#concatenate seglist
			newSegsList +=[seg+'_w'+str(i+1) for seg in fc[i].segsList[:]]
			for seg in fc[i].segsList:
				#concatenate segsDict
				newSegsDict[seg+'_w'+str(i+1)] = fc[i].segsDict[seg][:]
			newActivitys += fc[i].activitys[:]
			newSuprasegmentals += fc[i].suprasegmentals[:] if fc[i].suprasegmentals else [] #Note that suprasegmentals is now an empty list if there are none, instead of NoneType
#TODO change richCand() so that empty list is the default if there are no suprasegmentals
		newC = featureSet.featureToS(newSegsDict,newSegsList)
		obsProb = 1 if newC==obsOutput else 0

		fcs.append(richCand(newC,[],obsProb,newSegsDict,newSegsList,None,newActivitys,newSuprasegmentals,surfaceForm=newC))
		
	#Assign markedness violations to faithful candidates
	cs = [c.c for c in fcs]
	for fc in fcs:
		for con in constraints:
			fc.violations.append(con.assignViolations(fc,featureSet))

	allCands = fcs

	# Generate new candidates, dropping off at a rate controlled by A as you get farther down the 'tree' and rejecting them if they are not harmonically improving, according to s 	
	moarCandidates = 1
	t = 1
	A = .5
	s = 20 # sigmoid parameter
	while moarCandidates:
		for o in operations:
			for c in allCands:
				# apply o with probability A/t
				if random.random()<A/t:
					try:
						candidates = o(c,featureSet)
					except:
						print("Error, trying to apply operation  to candidate ", c)
					if type(candidates)==tuple:
						candidates, *_ = candidates
					#print(candidates)
					candidates = [c for c in candidates if c.c not in cs]
					# TODO check operations list also to establish sameness
					for possibleCand in candidates:
						for con in constraints:
								possibleCand.violations.append(con.assignViolations(possibleCand,featureSet))
						possibleCand.harmony = -sum(viol*weight for viol,weight in zip(possibleCand.violations,w))
						Hdiff = possibleCand.harmony - c.harmony
						p_keep = (1/2)*Hdiff/math.sqrt(s+Hdiff**2)+0.5
						if random.random()<p_keep:
							possibleCand.observedProb = 1 if possibleCand.surfaceForm==obsOutput else 0
							allCands.append(possibleCand)
							cs.append(possibleCand.c)
							
						

		t+=1
		if random.random()<(1-(A/t))**(len(operations)):
			#Halt candidate generation
			moarCandidates = 0
	
	# assign PFC violations:

	wNum = 0
	for l in lexemes:
		if l.PFCs:
			for pfc in l.PFCs:
				if wNum:
					for cand in allCands:
						# Have to actually make a copy to evaluate
						# fill in 'w2', 'w3' etc on segment labels on the candidates
						newPFC = PFC(pfc.w,pfc.feature,pfc.seg,pfc.seg2,pfc.typ)
						newPFC.seg = newPFC.seg+'_w'+str(wNum+1) if newPFC.seg else None
						newPFC.seg2 = newPFC.seg2+'_w'+str(wNum+1) if newPFC.seg2 else None
						cand.violations.append(newPFC.evaluate(cand))
						cand.harmony += -cand.violations[-1]*newPFC.w
				else:
					for cand in allCands:
						cand.violations.append(pfc.evaluate(cand))
						cand.harmony += -cand.violations[-1]*pfc.w
				constraintList.append(pfc.name)
				w.append(pfc.w)
		wNum+=1

	tab = Tableau("petitami")
	for cand in allCands:
		tab.addCandidate(cand)
	
	return tab,constraintList,w


# test code:





def diffCands(cbase,cdiff,skipChar='x'): # Use Damerau-Levenshtein distance, but with n features different as 'weights'
	# Takes richCand() objects
	# This code adapted from gist.github.com/badocelot/5327337
	# Explanation here: https://www.lemoda.net/text-fuzzy/damerau-levenshtein/index.html
	# assumes cbase and cdiff use the same feature sets, so their .segs dictionaries all have the same length of feature vectors
	# Used to prevent transposition for first characters
	INF = len(cbase.segsList)*len(list(cbase.segsDict.values())[0])+len(cdiff.segsList)*len(list(cdiff.segsDict.values())[0])
	
	# Matrix: (M+2) x (N+2)   M - len cbase, N - len cdiff
	matrix = [[INF for n in range(len(cdiff.segsList)+2)]]
	matrix += [[INF] + [i*len(list(cdiff.segsDict.values())[0])/2 for i in range(len(cdiff.segsList)+1)]]
	matrix += [[INF,m*len(list(cbase.segsDict.values())[0])/2] + [0]*len(cdiff.segsList) for m in range(1, len(cbase.segsList)+1)]

	
	#last_row = {} # Holds the last row each element was encountered
	
	# Matrix to hold the changes that were chosen at each step - two levels smaller than the distance matrix - no INF col, and ignoring the initialized epenthesis/deleiton columns
	# entries will be tuples (row_from,col_from,change)
	# change is a tuple too - (TYPE,[features that were added/deleted/overwritten])
	
	change_matrix = [[0]*(len(cdiff.segsList)+2) for m in range(len(cbase.segsList)+2)]
	# Fill in Deletion and Epenthesis changes into change_matrix
	i=2
	for seg in cdiff.segsList:
		change_matrix[1][i]=(1,i-1,('EPEN'))
		i+=1
	
	i=2
	for seg in cbase.segsList:
		change_matrix[i][1]=(i-1,1,('DEL',[f for f in cbase.segsDict[cbase.segsList[i-2]] if f[0]!=skipChar]))
		i+=1
		
	
	# Fill in costs
	for row in range(1, len(cbase.segsList) +1):
		seg_base = [f for f in cbase.segsDict[cbase.segsList[row-1]] if f[0] !=skipChar]
		print(seg_base)
		
		
		#last_match_col = 0  # column of last match on this row
		
		for col in range(1, len(cdiff.segsList)+1):
			seg_diff = [f for f in cdiff.segsDict[cdiff.segsList[col-1]] if f[0]!=skipChar]
			print(seg_diff)
			
			print(matrix[row][col])
			
			# fill in last row:
			#last_matching_row = last_row.get(tuple(seg_diff), 0)
			
			# cost of substitution
			d, ch1, ch2 = distSegs(cbase.segsDict[cbase.segsList[row-1]],cdiff.segsDict[cdiff.segsList[col-1]])
			cost = 0 if seg_base == seg_diff else d
			
			# compute substring distances
			feat_change = matrix[row][col]+cost
			epen = matrix[row+1][col] + len(seg_diff)/2
			delete = matrix[row][col+1] + len(seg_base)/2
			#TODO add as an option
			
			#transpose = matrix[last_matching_row][last_match_col]
			#+ (row - last_matching_row - 1)*len(list(cbase.segs.values())[0]) + 1
			#+ (col - last_match_col -1)*len(list(cbase.segs.values())[0])
			
			matrix[row+1][col+1] = min(feat_change,epen,delete) #,transpose)
			
			
			# order of assumptions: epen, delete, feature change, transposition
			# TODO: probly make this easily editable by the user
			if epen == matrix[row+1][col+1]:
				change_matrix[row+1][col+1] = (row+1,col,('EPEN'))  #,seg_diff)) #writing down seg_diff here is useless
				
			elif delete == matrix[row+1][col+1]:
				change_matrix[row+1][col+1] = (row,col+1,('DEL',seg_base))
				
			elif feat_change == matrix[row+1][col+1]:
				change_matrix[row+1][col+1] = (row,col,('CHANGE',ch2))
				
			#elif transpose == matrix[row+1][col+1]:
			#	change_matrix[row+1][col+1] = (last_matching_row,last_match_col,('TRANSPOSE')) 
			
			
			#matrix[row+1][col+1] = min(
			#	matrix[row][col] + cost, # feature changes
			#	matrix[row+1][col] +len(seg_diff),   # epenthesis
			#	matrix[row][col+1] +len(seg_base),   # deletion
				
				# transposition (metathesis)  NOTE: This assumes that any material between metathesized things is added/deleted
				#matrix[last_matching_row][last_match_col]
				#	+ (row - last_matching_row - 1)*len(list(cbase.segs.values())[0]) + 1
				#	+ (col - last_match_col -1)*len(list(cbase.segs.values())[0])
				#)
			
			#if cost ==0:
			#	last_match_col = col
				
		#last_row[tuple(seg_base)] = row
	#print(change_matrix, matrix)
	i,j,change = change_matrix[-1][-1]
	backtrace = [change]
	#print(i,j)
	while change_matrix[i][j]!=0:
		i,j,change = change_matrix[i][j]
		backtrace.append(change)
		#print(i,j,change)
		
	#Use segs identities from cbase, because that is the observed form, and therefore the form that we are trying to assert
	
		
	return matrix[-1][-1], matrix, change_matrix, backtrace
			
	


def inducePFCs(cbase,cdiff,featureSet,lamb = 5):
	'''Induce PFC's to prefer cbase over cdiff.  For now, this function only induces feature exists constraints, and feature on segment constraints.  Precendence constraints must be constructed later, after the diffCands() function includes a proper cost analysis for a transposition.
	
	lamb is the lambda value for the Poisson distribution over number of constraints that will be induced.  It's the mean number of constraints to induce.'''
	dist,m,chm,backtrace = diffCands(cbase,cdiff,skipChar=featureSet.skipChar)
	#Note: Deletions will not contain skipChar values, but feature changes will
	
	listOfPFCs = []
	for ch,seg in zip(backtrace[::-1],cbase.segsList):
		for f in ch[1]:
			# feature_on_segment
			listOfPFCs.append((10,f,seg))
			#TODO 10 is the initial weight of PFC's - a parameter of learning
			
			# feature exists
			listOfPFCs.append((10,f))
	print(listOfPFCs)
			
	nPFCs = np.random.poisson(lamb,1)[0]
	return random.sample(listOfPFCs,nPFCs)






			
def distSegs(s1,s2): # distance = n features that are different
	''' takes two lists of features, and compares them '''
	#Note: this one has to take in full feature sets with skipChar values intact.
	#The idea: a change from specified to unspecified 'counts' as a change just as much as 0-1 or 1-0
	s1_not_s2 = [i for i in s1 if i not in s2]
	s2_not_s1 = [i for i in s2 if i not in s1]
	if len(s1_not_s2) == len(s2_not_s1):
		dist = len(s1_not_s2)
	else:

		dist = "ERROR"
	return dist, s1_not_s2, s2_not_s1

	
	

def exampleCand2():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg3 = [(0,"back"),(0,"high"),(0,"front"),(0,"low")]  # ah
	segs = {"seg1":seg1,"seg3":seg3}
	order = ["seg1","seg3"]
	user_defined = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return candidate(1,segs=segs,order=order,user_defined=user_defined)

def exampleCand3():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg3 = [(0,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg3":seg3} 
	order = ["seg1","seg3"]
	user_defined = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return candidate(1,segs=segs,order=order,user_defined=user_defined)

def exampleCand4():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg3 = [(0,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg3":seg3}
	order = ["seg1","seg3","seg1","seg3"]
	user_defined = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return candidate(1,segs=segs,order=order,user_defined=user_defined)

def exampleCand5():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	seg2 = [(1,"back"),(1,"high"),(0,"front"),(0,"low")]  # u
	seg3 = [(0,"back"),(0,"high"),(0,"front"),(1,"low")]  # a
	segs = {"seg1":seg1,"seg2":seg2,"seg3":seg3}
	order = ["seg1","seg2","seg3"]
	user_defined = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return candidate(1,segs=segs,order=order,user_defined=user_defined)

def exampleCand6():
	seg1 = [(0,"back"),(1,"high"),(1,"front"),(0,"low")]  # i
	segs = {"seg1":seg1}
	order = ["seg1","seg1"]
	user_defined = [(0,"stress1syll"),(1,"stress2syll"),(0,"stress3syll")]
	return candidate(1,segs=segs,order=order,user_defined=user_defined)

		
		
		
		