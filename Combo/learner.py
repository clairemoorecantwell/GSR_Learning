#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import math
import numpy as np
from itertools import chain
import itertools
import re
import random
import sys



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
		# Always add morphBoundary as a possible segment.  it is 0 for everything, except the 'morphBoundary' feature
		# TODO revisit whether it is better to store the morpheme boundary differently in some way?
		self.featureNames.append("morphBoundary")
		for seg in self.featureValues:
			self.featureValues[seg].append("0")
		self.featureValues["_"]=[skipChar for i in self.featureNames]
		self.featureValues["_"][-1]='1'

	#TODO make a str() function

	#TODO check for underspecified segments, or for redundant features

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
		'''skips _ in segs dictionary, but retains it in segment order'''
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
			#if string[i]=="_":
			#	segs["_"] = [('1','morphBoundary')] # give this guy a feature
			#	order.append("_")
			#else:
			segs[k]=[j for j in zip(self.featureValues[string[i]],self.featureNames)]
			order.append(k)

		return segs,order

	def featureToS(self,segs,order):
		'''converts a segment dictionary and an ordering to a string '''
		S = [] # in which to store the segments as we find them
		for s in order: # go through the segment labels in order
			#if s != "_":
			S.append(self.exists(segs[s],add=True))
			#else:
			#	S.append("_")
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

	def copy(self):
		newC = candidate(self.c,self.violations[:],self.observedProb,self.surfaceForm)
		newC.harmony = self.harmony
		newC.predictedProb = self.predictedProb
		return newC

	def toRichCand(self,features):
		segsDict, segsList = features.stringToF(self.c)
		return richCand(self.c,self.violations[:],self.observedProb,segsDict,segsList,surfaceForm =self.surfaceForm)

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
	def __init__(self,tag,prob=1,hiddenStructure=False,lexemes = [],w = []):
		self.tag = tag # Human-readable tag to let the user know which tableau this is
		self.prob = prob # Corresponds to tab.prob in input file
		self.candidates = [] # To be filled during tableau creation
		self.faithCands = [] # 1 if the candidate is 'faithful', 0 otherwise
		self.probDenom = 1 # denominator for calculating MaxEnt prob of each candidate
						   # this is the sum of each exponentiated harmony score
		self.predProbsList = [] # list of each candidate's predicted probability; used in sampling
								# gets filled (and updated) during learning
		self.obsProbsList = [] 	# list of each candidate's observed probability; used in sampling
		self.HList = [] # list of each candidate's harmony; for straight or Noisy HG
		self.winner = None
		self.constraintList = None # this will generally wind up being a bunch of strings, followed by a bunch of tuples, for the PFCs
		self.hiddenStructure = hiddenStructure
		self.surfaceCands = [] # a place to hold the unique surface candidates
		# Note: if hidden structure is active, then obsProbsList corresponds to surfaceCands.
		# Otherwise, it corresponds simply to candidates
		self.lexemes = lexemes  # only required for applyPFCs()
		self.w = w
		self.pfcIndex = len(self.w)
		self.negCrossEntropy = 0 #Just for this tableau.  Can multiply by self.prob to get neg log likelihood
	def __repr__(self):
		return "Tableau object '" + self.tag + "' with " + str(len(self.candidates)) + " candidates.  Winner: " + str(self.winner) + "\n" + "Attributes: tag, prob, candidates, probDenom, predProbsList, HList, obsProbsList, surfaceCands, hiddenStructure, constraintNames, winner"
	def __str__(self):
		vform = '{:4s} '   #format function for tableau - increase number for more space between cells
		longCand = max([len(i.c) for i in self.candidates])
		cform = '{:>'+str(longCand)+'s} '
		form = '{:3s} ' + cform + '{:5s} '*3 + vform*len(self.candidates[0].violations)
		out = "Tableau " + self.tag + "\n"
		# expect constraintNames to be a list of strings
		if self.constraintList:
			names = [i[0] if type(i)==tuple else i for i in self.constraintList ]
			print(names)
			vform = ''.join([('{:^' + str(len(i)) + 's} ') for i in names])
			form = '{:3s} ' + cform + '{:5s} '*3 + vform
			out += form.format(*[" "]*5 + [str(j) for j in names])
		for i in range(0, len(self.candidates)):
			w = " "
			if self.candidates[i-1].c == self.winner:
				w = " --> "
			v = self.candidates[i-1].violations
			row = [w] + [self.candidates[i-1].c,self.candidates[i-1].observedProb,self.predProbsList[i-1],self.HList[i-1]] + v
			out += '\n' + form.format(*[str(j) for j in row])
		return out
	def toFile(self,w):
		#calculate harmonies, and predicted values
		# add in constraint weights, including PFC weights
		# add in lexeme labels somewhere
		# create an 'input' column
		self.predictProbsMaxEnt(w)
		out = '\t'.join(["input","candidate","obs.prob","pred.prob","H"]+[i[0] if type(i)==tuple else i for i in self.constraintList])
		out += '\n' + '\t'.join(["","","","",""]+[str(j) for j in w])
		for c in self.candidates:
			out += '\n' + '\t'.join([str(j) for j in [self.tag,c.c,c.observedProb,c.predictedProb,c.harmony]+c.violations])

		return out

	def copy(self):
		newT = Tableau(self.tag,self.prob,self.hiddenStructure,self.lexemes[:],self.w[:])
		newT.winner = self.winner
		newT.constraintList = self.constraintList
		for c in self.candidates:
			newT.addCandidate(c.copy())

		return newT



	def addCandidate(self,cand):
		self.candidates.append(cand)
		# Is this a faithful candidate?
		#
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

	def applyPFCs(self):
		self.pfcIndex = len(self.w)
		# fill out constraintList with placeholders if it's not long enough
		if len(self.constraintList)<len(self.w):
			self.constraintsList+=["C"]*(len(self.w)-len(self.constraintList))
		if len(self.constraintList)>len(self.w):
			print("WARNING: you have more constraint names than constraint weights in tableau " + self.tag)

		for lexeme in self.lexemes:
			for pfc in lexeme.PFCs:
				#print(pfc.name)
				for cand in self.candidates:
					parsed = cand.c.split("_")
					try:
						cand.violations.append(pfc.evaluate(parsed[self.lexemes.index(lexeme)]))
					except:
						print("Failed to apply PFC: "+pfc.name)
				self.constraintList.append((pfc.name,pfc))
				self.w.append(pfc.w)

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
			winCandidate = matchCands[0]

		return winCandidate
	def getObsOutput(self):
		''' simple function to get the observed output from the obsProbsList'''
		obsOutput = self.surfaceCands[np.random.choice(range(0,len(self.surfaceCands)),1,p=self.obsProbsList)[0]]
		return obsOutput

	def compareObsPred(self,w,theory='MaxEnt'):
		predCandidate=self.getPredWinner(w=w,theory=theory)
		obsCandidate=self.getObsCandidate(w=w,theory=theory)
#		for c in self.candidates:
#			 if c.c==obs:
#				 obsCandidate = c
# ^^ why is this here?  Is it necessary for something?

		error = (0 if obsCandidate.surfaceForm==predCandidate.surfaceForm else 1)

		return error, obsCandidate, predCandidate


class Grammar:
	def __init__(self,filename,featureSet,constraints=None,operations=None,generateCandidates=False,addViolations=False,PFC_type="none"):
		self.trainingData = trainingData(filename)  # A list of lists. Each entry is [[lexeme1,lexeme2,...],'correctSurface','UR']
		self.featureSet = featureSet
		self.constraints = constraints
		self.operations = operations # Read these off the top of the input data file.
		self.w = [] # Weights, starts empty
		self.t = 0	# For learning, t starts at 0
		self.learningRate = 0.01
		self.activityUpdateRate = 0.05
		self.PFC_lrate = 0.1
		self.PFC_startW = 10
		self.PFC_decay = 0.0001

		self.decayRate = 0.001

		self.generateCandidates = generateCandidates # defaults to False, meaning you'll use the given candidates IF they exist
		self.addViolations = addViolations # whether or not to use the constraint file to add extra violations to each candidate
		self.PFC_type = PFC_type # options are "none", "pseudo", "full"
		self.lexC_type = 0 #If it's a number, that's the max number of copies allowed for each constraint
		self.pChangeIndexation = 0.5 # probability of changing a lexical item's indexation, rather than upating the weight
		#self.maxLexCs = 4
		self.lexCStartW = 5
		self.lexCs = []

		self.p_useListed = 0  # If greater than 2, create a hidden structure tableau; if 0 don't allow lexical listing of whole forms at all
		self.pToList = 0.75
		if self.p_useListed>0:
			self.cPairs = self.prepForUselisted() # this is a tuple, the second member is the reverse sorted _listed indices, for removing
			#Now, the _listed versions have been removed from the constraint names vector
		self.initializeWeights() # Initialize weights when Tableaux object is created (to zero, or some other vector depending on how you call this function.)
		if self.lexC_type:
			self.prepForLexC()

	def prepForUselisted(self):
		UseListedIndex = None
		if self.p_useListed>=2:
			self.trainingData.constraintNames.append("UseListed")
			UseListedIndex = self.trainingData.constraintNames.index("UseListed")
			print("adding UseListed at index"+str(UseListedIndex))
			# add a 1 for 'useListed' for every candidate in self.trainingData.tableaux
			# we're assuming all candidates are unlisted at the start
			for t in self.trainingData.tableaux:
				for c in t.candidates:
					c.violations.append(1)

		# create a list of tuples pairing up plain and listed versions of each relevant constraint
		indexPairs = []
		toRemove = []
		for name in self.trainingData.constraintNames:
			if re.search("_listed",name):
				cname = re.sub('_listed','',name)
				indexPlain = self.trainingData.constraintNames.index(cname)
				indexListed = self.trainingData.constraintNames.index(name)
				indexPairs.append((indexPlain,indexListed))
				toRemove.append(indexListed)

		toRemove = sorted(toRemove,reverse=True)
		for i in toRemove:
			self.trainingData.constraintNames.pop(i)
		return indexPairs,toRemove,UseListedIndex

	def prepForLexC(self):
		self.lexCs = [[0] for i in self.w]
		# create a vector for every constraint
		# go through the lexicon, add in index vectors
		for lex in self.trainingData.lexicon.values():
			lex.lexCindexes = [0 for i in self.w]

		if self.lexC_type == "inf":
			self.lexC_type = length(self.trainingData.lexicon)**2
			# make the max length the length of the lexicon squared.  Hopefully this is long enough to accommate whatever weird stuff you're up to!


	def createLearningPlaylist(self,n):
		# n is total number of learning simulations
		return [self.trainingData.learnData[i] for i in list(np.random.choice(range(0,len(self.trainingData.learnData)),n,p=self.trainingData.sampler))]
	def initializeWeights(self,w=None):
		'''Function to initialize the weights - can take an argument, which is hopefully the same length as the number of constraints in the Tableaux object.  If it doesn't get that argument, it will initialize them to zero. '''
		# TODO (low priority atm) Add functionality to initialize weights to random values
		# figure out how many constraints we have all together
		nC = len(self.trainingData.constraintNames) + (len(self.constraints) if self.constraints else 0)
		if w is None:
			self.w = [0]*nC
		else:
			if len(w)==nC:
				self.w=w
			else:
				print("ERROR: you tried to initialize weights with a list of length ", len(w), ", but you have a total of ", nC, " constraints.  addViolations is set to ", self.addViolations)
				# This will print a warning, but it won't actually stop you from initializing constraints badly?  Maybe this is a problem that should be fixed.

	def calculate_sample_weights(self,frequencies):

		#helper function; calculates weights for the weighted sample
		#takes a list of word frequencies as input
		#returns a set of weights

		total = sum(frequencies)
		weights = [ round(freq / total, 10) for freq in frequencies]
		return weights


	def update(self,datum): # datum is an entry from playlist
		# Start with a learning datum
		lexemes = datum[0]


		# TODO this code is recapitulated inside Grammar.makeTableau()
		# streamline?
		if self.p_useListed==0: #If we're not doing useListed at all
			# Note that we've encountered these two lexemes
			for lex in lexemes:
				lex.lastSeen = self.t
				lex.freq += 1

			# Decay the existing PFCs affiliated with each lexeme, and remove zero weighted ones
			for lex in lexemes:
				lex.decayPFC(self.t,self.PFC_decay,decayType="static")
				if len(lex.PFCs)>len(self.featureSet.featureNames)*len(lex.segLabels)*4:
					print("WARNING: too many PFCs")
					break

		if self.lexC_type:
			#print("decaying")
			for c in range(0,len(self.lexCs)):
				self.lexCs[c] = [i-self.decayRate for i in self.lexCs[c]] # decay all lexC's
				self.lexCs[c] = [i if i>0 else 0 for i in self.lexCs[c]]  # lower bound at zero
			#print(self.lexCs)

		# grab, create, or fill out the tableau
		tab= self.makeTableau(datum)

		# Predict an output and compare to observed
		e, obs, pred = tab.compareObsPred(tab.w)


		#print(constraintList)
		if e:
			#print(e,tab.tag, obs.c,pred.c,obs.violations,pred.violations,obs.harmony,obs.predictedProb,pred.harmony,pred.predictedProb)
			#print(self.w)
			#################################################################
			# update general weight: perceptron update
			updateVector = [float(p)-float(o) for p,o in zip(pred.violations, obs.violations)]
			self.w = [float(wt)+up*self.learningRate for wt,up in zip(self.w,updateVector) ]
			self.w=[i if i>0 else 0 for i in self.w] # limit to positve constraint weights
			#################################################################
			#print(self.w)

			#################################################################
			# useListed
			if self.p_useListed>0:
				# TODO figure out what to do with within-item variation
				if random.random()<self.pToList:
					self.trainingData.lexicon["_".join([i.tag for i in datum[0]])] = lexeme("_".join([i.tag for i in datum[0]]),[character for character in obs.surfaceForm])
			##################################################################

			##################################################################
			# Lexically-indexed constraints
			for u in [j for j in range(0,len(updateVector)) if updateVector[j]!=0]: # go through constraints that matter
				# u is an index, into constraints and violations, and indexation values on lexemes
				weights = self.lexCs[u][1:]  # vector of indexed C's for that constraint; empty if there are none
				if weights and updateVector[u]>0:
					mx = max(weights)
					mn =False
				elif weights and updateVector[u]<0:
					mn = min(weights)
					mx =False
				else:
					mn =False
					mx =False

				obsParsed = obs.c.split("_")
				predParsed = pred.c.split("_")
				if len(obsParsed)!=len(predParsed) or len(obsParsed)!=len(datum[0]):
					print("predicted: "+pred.c)
					print("observed: " + obs.c)
					print(datum[0])
					print(" Error: predicted and/or observed cannot be aligned with lexemes - LexC induction will not work")
					exit

				updateIndices = []
				for i in range(0,len(datum[0])):
				# find the lexeme that differs between obs and pred
				# and update it and adjacent lexemes only
					if obsParsed[i] != predParsed[i] and i not in updateIndices:
						updateIndices.append(i)
					if i>0 and i-1 not in updateIndices: # if we're not already updating the previous lexeme
						updateIndices.append(i-1)
					if i<len(datum[0])-1 and i+1 not in updateIndices:
						updateIndices.append(i+1)


				# now updateIndices is just a list of indices of lexemes which need to be updated
				for i in updateIndices:
					lex = datum[0][i]
					currentIndex = lex.lexCindexes[u] -1 # they start from 1
					w = weights[currentIndex] if weights else 0 # current weight of the lexC indexed to this lexeme
					if w==0:  # if a lexC has decayed to zero, it counts as not-existent and is removed from the lexeme
						lex.lexCindexes[u] = 0
						currentIndex = -1
						#print("re-indexed to 0")
					if random.random()<self.pChangeIndexation: # yes, we change indexation
						#print("change Indexation...")
						# the indexed C exists AND it is not the min/max already
						# if currentIndex is not -1, then weights should not be []
						# TODO add error-checking for this^

						if currentIndex>=0 and w!=mx and w!=mn:
							# note that whichever (max or min) is not applicable will equal False, not a number
							# we know we need to switch indexation

							s = sorted(weights[:])
							currentSpotInSort = s.index(w)
							if mx: # obs preferring; move to next greater weight
								direction = 1
							else: # pred preferring; move to next lower weight
								direction = -1

							move = 1
							while move:
								newWeight = s[currentSpotInSort+direction*move]
								if newWeight!=w:
									move = 0
								else:
									move += 1

							# change the index on the lexeme to the location of that new weight
							lex.lexCindexes[u]=weights.index(newWeight)+1 # plus 1 because we're indexing into the original lex weight vector
							#print("re-indexed from "+str(currentIndex+1) + " to "+str(lex.lexCindexes[u]))
							# re-indexed!

						elif len([w for w in weights if w>0])<self.lexC_type and not mn: # either the weight doesn't exist, or it's already at the min/max
							# only induce if at the max
							# still check whether we've already capped out our allowed number of weights
							# Induce at the first index that's 0, or append to end
							newIndex = 0 if 0 not in weights else weights.index(0)+1
							if newIndex: # we're re-populating a slot that got decayed to zero
								self.lexCs[u][newIndex] = self.lexCStartW
								lex.lexCindexes[u]=newIndex
							else: # we're appending
								self.lexCs[u].append(self.lexCStartW) # add a new lexC
								lex.lexCindexes[u]=len(self.lexCs[u])-1 # index to the new weight
							print("New cloned copy of "+self.trainingData.constraintNames[u])

						elif currentIndex>=0: # Should only get here if we SHOULD induce but have already reached the max
							# just update
							# if weight needs to be lower than min, will just get updated down
							# don't proceed if there is no lexC affiliated with this lexeme
							self.lexCs[u][currentIndex+1] += updateVector[u]*self.learningRate
							#print("updating at index "+str(currentIndex+1))

					else: # we don't change indexation
						if currentIndex>=0 and weights and weights[currentIndex]: # if lexC exists
							# update
							self.lexCs[u][currentIndex+1] += updateVector[u]*self.learningRate
							#print("updating at index "+str(currentIndex+1))

					##############################
					# Decided not to do this part, because of Pater 2010
					# Need lexemes to be able to dictate what happens outside their borders for Yine
					# figure out which lexeme(s) differ
					# only apply new clones to lexemes that differ
					#parsed = obs.c.split("_")
					#parsedPred = pred.c.split("_")
					#if len(parsed)!=len(datum[0]) or len(parsedPred)!=len(datum[0]):
					#	print(parsed)
					#	print(datum[0])
					#	print("ERROR: lexical indexation cannot be induced because morphemes in the candidate cannote be aligned with morphemes in the input")
					#	exit
					#for i in range(0,len(datum[0])):
					#	if parsed[i]!=parsedPred[i]:
					#		#Ok, now we will change the indexation of lexeme i
					#		etcetera
					# TODO possible way to split the difference on locality:
					# find the lexeme(s) that differ from obs to pred, and only update those and adjacent lexemes



			##################################################################


			##################################################################
			# PFC stuff
			# update existing PFCs
			if self.PFC_type !='none':
				for pfc,p,o in zip(tab.constraintList[tab.pfcIndex:],pred.violations[tab.pfcIndex:],obs.violations[tab.pfcIndex:]):
					pfc[1].w+=(p-o)*self.PFC_lrate
					pfc[1].w = 0 if pfc[1].w<0 else pfc[1].w

				# induce new PFCs
				newPFCs = []
				if self.PFC_type=="pseudo":
					# parse each candidate into morphemes
					parsed = obs.c.split("_")
					parsedPred = pred.c.split("_")
					if len(parsed)!=len(datum[0]) or len(parsedPred)!=len(datum[0]):
						print(parsed)
						print(datum[0])
						print("ERROR: pseudo-PFC cannot be induced because morphemes in the candidate cannote be aligned with morphemes in the input")
						exit
					for i in range(0,len(datum[0])):
						if parsed[i] != parsedPred[i]: #localize the error to the morpheme we are considering
							newPFC = PFC(self.PFC_startW,surfaceString=parsed[i])
							if newPFC not in datum[0][i].PFCs:
								datum[0][i].PFCs.append(newPFC)
								print("Added ", datum[0][i].tag, newPFC.name)


				elif self.PFC_type=="full":
					newPFCs = inducePFCs(obs,pred,self.featureSet)
					#pfcs_to_words = [[]]*len(datum[0])
					for pfc in newPFCs: #loop through and determine which goes with which lexeme
						if len(pfc)>2:
							wd = re.search('(_)(w)([1234567890])',pfc[2])
							if wd:
								newPFC = PFC(self.PFC_startW,pfc[1],re.sub('_w.*','',pfc[2]))
								if newPFC not in datum[0][int(wd.groups()[2])-1].PFCs:
									#print("yes")
									datum[0][int(wd.groups()[2])-1].PFCs.append(newPFC)
							else:
								newPFC = PFC(self.PFC_startW,pfc[1],pfc[2])
								if newPFC not in datum[0][0].PFCs:
									#print("yes")
									datum[0][0].PFCs.append(newPFC)
						else:
							for lex in datum[0]:
								newPFC = PFC(self.PFC_startW,pfc[1])
								if newPFC not in lex.PFCs:
									lex.PFCs.append(newPFC)
								#somewhat odd strat: affiliate exists_feature constraints with all lexemes



				# induce PFCs
				# compare against existing PFCs
				# update if they already exist, otherwise induce
				# Don't update every PFC???
			##################################################################


		self.t+=1
		#print(self.w)
		return e

	def epoch(self,playlist,niter,start=0):
		errors = 0
		for i in range(0,niter):
			errors+=self.update(playlist[start+i])
			#print(start+i)

		error_rate = errors/niter

		# print out list of weights (to file)
		# print out SSE
		# print out likelihood
		#
		return error_rate

	def learn(self,nIterations,nEpochs,outFile = "output.txt"):
		grammar_constraints_w = []
		PFCs_w = []
		PFC_list = [] #stores every PFC that is ever induced

		playlist = self.createLearningPlaylist(nIterations*nEpochs)
		#print(playlist)
		for i in range(0,nEpochs):
			rate = self.epoch(playlist,nIterations,start=nIterations*i)
			print(rate)

			grammar_constraints_w.append(self.w)
			currentPFC_w = [0 for i in PFCs_w[-1]] if len(PFC_list)>0 else []
			for lexeme in self.trainingData.lexicon.values() :
				if type(lexeme)=='lexeme':
					for pfc in lexeme.PFCs:
						name = lexeme.tag + "_" + pfc.name
						if name not in PFC_list:
							PFC_list.append(name)
							currentPFC_w.append(0) # make it the right length to accommodate the new PFCs
						currentPFC_w[PFC_list.index(name)] = pfc.w
			PFCs_w.append(currentPFC_w)

		results = []
		resultsData = []
		for datum in self.trainingData.learnData:
			if datum[0] not in resultsData:
				resultsData.append(datum[0])  #datum[0] is the list of lexemes as the input e.g. [paN, po?ok]
				tab = self.makeTableau(datum)
				results.append(tab.toFile(tab.w))

		with open("output.txt",'w') as f:
			f.write('\n'.join(results))

		with open("weights.txt","w") as f:
			print(grammar_constraints_w)
			out = ""
			for ep in grammar_constraints_w:
				out +="\n" + "\t".join([str(w) for w in ep])
			f.write(out)

		#print("learning complete")
		with open("PFCs.txt","w") as f:
			out = "\t".join(PFC_list)
			for ep in PFCs_w:
				out +="\n" + "\t".join([str(pfc) for pfc in ep]+["0" for i in PFC_list[len(ep):]])
			f.write(out)


	def makeTableau(self,datum):
		'''Make the tableau for learning, given all the parameters'''
		''' datum is an entry in a trainingData.learnData object'''
		''' it has the form [[lexeme1,lexeme2,...],surface string, input string]'''
		method = "deNovo"
		# "deNovo": create a brand new tableau, with generated candidates.  For this we need operations, and constraints defined as functions
		# "partial": use user-defined candidates, but add violations of a few markedness constraints
		# "full": completely user-defined, except for perhaps the PFCs

		# Determine the creation method, and make sure we have everything for it
		# Right now only "full" is implemented
		if not self.generateCandidates:
			if not self.addViolations:
				method = "full"
			elif self.constraints:    # constraint functions must exist for them to be used to assign new violations
				method = "partial"
			else:
				print ("ERROR: you must define a set of constraint functions")
				exit
		else:
			if self.constraints and self.operations:
				# TODO fill this out for UseListed; it might not work as expected at the moment.
				return createTableau(lexemes,self.constraints,self.operations,self.featureSet,datum[1],w=self.w[:])
			else:
				print("ERROR: you cannot generate candidates without predefined operations and constraints")

		# Initial tableau creation, from the input file
		tab = self.trainingData.tableaux[self.trainingData.tableauxTags.index(datum[2])].copy()
		tab.w = self.w[:]
		tab.constraintList = self.trainingData.constraintNames[:]
		#print(tab)

		############################### UseListed tableau creation
		#listed = False # Are we using a specially listed lexical item?  If False, we compose from extant lexical items

		# Check if we should use a listed form - is there a listed form in the lexicon?
		listedTag = "_".join([i.tag for i in datum[0]]) if len(datum[0])>1 else False
		r = random.random() # sample to determine whether we do listing or composition on this particular trial
		if listedTag in self.trainingData.lexicon and 1<self.p_useListed<2: # we're sampling based on frequency
			f_composed = [lex.freq for lex in datum[0]]
			f_listed = self.trainingData.lexicon[listedTag].freq
			#########################################################
			## To change how listed forms are sampled based on frequency edit here
			#########################################################
			# choose the lowest frequency lexeme of the bunch
			local_p_useListed = f_listed/(f_listed + min(f_composed))

			# choose the root's frequency, if there is exactly one root
			#roots = [1 if lex.kind =='root' else 0 for lex in datum[0] ]

			#if sum(roots) == 1:
			#	f_root = f_composed[roots.index(1)]
			#	local_p_useListed = f_listed/(f_listed + f_root)
			#else:
			#	local_p_useListed = f_listed/(f_listed + min(f_composed))
			#########################################################
			print("f_composed:"+str(f_composed))
			print("f_listed:"+str(f_listed))
			print("p_uselisted")
			print(local_p_useListed)
		else:
			local_p_useListed = self.p_useListed
		if listedTag and listedTag in self.trainingData.lexicon and r< local_p_useListed:
			# we're just updating BOTH the parts and the whole listed form's frequency
			# (Parts updated above, in the main learning loop)
			self.trainingData.lexicon[listedTag].lastSeen = self.t
			self.trainingData.lexicon[listedTag].freq +=1

			# Check if we are using hidden structure to do this, or choosing between listing and composing
			if self.p_useListed>=2: # for now, set p_uselisted to 2 or higher to indicate "use hidden structure"
				# Build hidden structure tableau
				# note candidates as coming from one lexeme or another
				# and copy candidates over
				for lex in datum[0]:
					lex.lastSeen = self.t
					lex.freq += 1
				origCandidates = tab.candidates[:]
				for cand in origCandidates:
					newC = cand.copy()
					cstring = cand.c
					newC.c = "listed_"+cstring
					cand.c = "composed_"+cstring

					# self.cPairs is a tuple (list_of_pairs, reverse_sorted_indices_of_listed, UseListed violation index before _listed removal)
					newC.violations[self.cPairs[2]] = 0
					cand.violations[self.cPairs[2]] = 1

					for pair in self.cPairs[0]:  # assign violations of faith to _listed versus not
						# the tuple is (composedIndex,listedIndex)
						newC.violations[pair[0]] = newC.violations[pair[1]]  # set both columns to the _listed version
						cand.violations[pair[1]] = cand.violations[pair[0]]  # set both columns to the regular (composed) version

					for i in self.cPairs[1]: # Now remove the violation corresponding to the _listed form of the constraint
						newC.violations.pop(i)
						cand.violations.pop(i)

					tab.addCandidate(newC)


			elif r< local_p_useListed:  # Only using the listed form in the tableau
				print("Using the listed form only!")
				useListedIndex = self.cPairs[2]
				for cand in tab.candidates:
					if useListedIndex != None:  # If the useListed constraint exists (for hidden structure only)
						cand.violations[self.cPairs[2]] = 0 # setting the value for UseListed
					for pair in self.cPairs[0]:
						cand.violations[pair[0]] = cand.violations[pair[1]] #Only use the _listed version
					for i in self.cPairs[1]:
						cand.violations.pop(i)


				#lexemes = self.trainingData.lexicon[listedTag]


		else:
			'''no listed form - can get here 3 ways:
			(1) if listing is turned off (p_useListed ==0)
			(2) if listing was not selected on this trial
			(3) if the listed version isn't in the lexicon yet
			# exclude listeds if there are any - simply delete the column from the tableau
			# remove their violations from every candidate
			'''
			for lex in datum[0]:  # This little bit is redundant with above, and also in the main update() loop
				lex.lastSeen = self.t
				lex.freq += 1
			if self.p_useListed:
				for cand in tab.candidates:
					for i in self.cPairs[1]:
						cand.violations.pop(i)


		#################################################################################

		######################################################################
		# Adjust for lexically indexed C's
		if self.lexC_type:
			for cIndex in range(0,len(tab.w)): # run through all constraints
				wToUse = 0
				for lex in datum[0]: # run through all lexemes
					lexIndexForC = lex.lexCindexes[cIndex] # which idex does lex use?
					thisW = self.lexCs[cIndex][lexIndexForC] # what's the weight associated with that index?
					if thisW > wToUse: # if it's larger than we've seen before
						wToUse = thisW # keep it
				if wToUse: # if there was any weight above 0
					tab.w[cIndex]=wToUse # use that clone weight instead of the base weight

		######################################################################



		if method == "partial":
			# Assign violations of dynamic constraints
			tab.constraintList +=[c.name for c in self.constraints]
			for cand in tab.candidates:
				for con in self.constraints:
					cand.violations.append(con.assignViolations(cand,self.featureSet))

		#tab.applyPFCs()

		return tab#, tabconstraintList, w


		#def listForm(lexemes_list,lexicon):


class lexeme:
	def __init__(self, tag, segmentList = None, kind=None):
		self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
		self.segmentList = segmentList if segmentList else [i for i in tag]  # Human-readable list of segments, corresponding to feature lookup tables, if using
		self.segLabels = [self.segmentList[0]]+[self.segmentList[i] if self.segmentList[i] not in self.segmentList[:i] else self.segmentList[i]+str(i) for i in range(1,len(self.segmentList))] #create list of unique segment labels, to be used in candidate generation and evaluation by PFCs
		self.activitys = [1 for i in self.segmentList] # List of float value activity levels for self.segs.  Defaults to 1 for all
		self.linearSegOrder = [i for i in range(1,len(self.segmentList)+1)] # integers specifying the linear order of segs in self.segs. starts at 1
		# Example: t/z/n ami:
		# self.segs = ['t','z','n','a','m','i']
		# self.activitys = [.4, .5, .6, 1, 1, 1]
		# self.linearSegOrder = [1, 1, 1, 2, 3, 4]
		self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc. Optional
		self.freq = 1   #initialize at zero, increase during learning.  This number reflects the actual frequency of the lexeme during learning, rather than the frequency in the training data
		self.PFCs = [] # list of PFC objects, optional.
		self.lexCindexes = [] # list of indexation values for lex C's, indexing into Grammar.lexCs
		self.lastSeen = 0

	def __str__(self):
		out = 'Lexeme ' + str(self.tag) +' (' + str(self.kind) + ', f:' + str(self.freq) + ' )\n'
		segform = '{:2s} '*len(self.segmentList)
		out += segform.format(*self.segmentList)
		out += '\n'
		out += segform.format(*[str(i) for i in self.activitys])
		out += '\n'
		out += segform.format(*[str(i) for i in self.linearSegOrder])
		out += '\n'
		out += ''.join([i.name+": "+str(i.w)+'\n' for i in self.PFCs]) if self.PFCs else 'No PFCs'
		return out

	def __repr__(self):
		r = ""
		if self.kind!=None:
			r = ' - '+str(self.kind)
		return self.tag+r

	def decayPFC(self,t,decayRate,decayType='static'):
		for pfc in self.PFCs:
			if decayType=='static':
				pfc.w-=(float(t)-self.lastSeen)*decayRate
			elif decayType=='L1':
				for i in range(self.lastSeen,t):
					pfc.w -=decayRate*pfc.w
			elif decayType=='L2':
				for i in range(self.lastSeen,t):
					pfc.w -=(decayRate/2)*(pfc.w**2)
		self.PFCs = [pfc for pfc in self.PFCs if pfc.w>0]

	def toRichCand(self,featureSet):
		''' produces the faithful candidate for just this one lexeme, given a Feature object, featureSet '''
		#TODO first check that all segments are even in featureSet

		#Now, get the segments in all possible orders
		segsInOrder = []
		segLabelsInOrder = []
		for i in range(1,max(self.linearSegOrder)+1):
			indices = [index for index,value in enumerate(self.linearSegOrder) if value ==i]
			if len(indices)>0:
				segsInOrder.append([self.segmentList[i] for i in indices])
				segLabelsInOrder.append([self.segLabels[i] for i in indices])
		cands = list(itertools.product(*segLabelsInOrder))
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
	def __init__(self,w,feature=None,seg=None,seg2=None,surfaceString=None,typ='feature_on_segment'):
		self.w = w
		self.feature = feature # must be a tuple (0, 'high'), (1, 'coronal') etc.
		self.seg = seg  # name of a seg in the lexeme that this PFC belongs to
		self.seg2 = seg2 # note that seg names must be immutable in the lexeme!
		self.surfaceString = surfaceString # the surface string to match if it's a pseudoPFC
		self.typ = typ # typ can be 'feature_on_segment', 'exists_feature', 'prec', 'suprasegmental', or 'pseudo'

		# auto-calculate PFC type
		# note that type 'suprasegmental' must be defined by the function call, and cannot be specified within (it can't be distinguished in form from exists_feature)
		if feature is None and seg is not None and seg2 is not None:
			self.typ = 'prec'
			self.name = seg+'<<'+seg2

		elif feature is not None and seg is None and seg2 is None and typ!='suprasegmental':
			self.typ = 'exists_feature'
			self.name = str(feature)

		elif surfaceString is not None and feature is None and seg is None and seg2 is None:
			self.typ = 'pseudo'

		elif feature is not None and typ=='suprasegmental':
			pass
		elif feature is not None and seg is not None and typ=='feature_on_segment':
			pass
		else:
			print("ERROR: you tried to create an impossible type of PFC.")
			exit()

		self.name = '_'.join([str(param) for param in [feature,seg,seg2,surfaceString] if param])

	def __eq__(self,other):
		same = 0
		if self.feature == other.feature and self.seg == other.seg and self.seg2 ==other.seg2 and self.surfaceString==other.surfaceString:
			same = 1
		return same

	def __str__(self):
		return self.name

	def evaluate(self,cand): #evaluates a richCand object, or a simple string for a pseudoPFC
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
		elif self.typ == 'pseudo':
			# this one evaluates a string, pre-parsed out of a cand object
			viol = 0 if self.surfaceString == cand else 1
		else:
			print("Error!  You've passed the PFC something that's not a valid type.  Types are 'feature_on_segment', 'prec', 'exists_feature', 'suprasegmental'")
		return viol

#TODO more thorough testing of PFC functionality

class trainingData:
	'''essentially, a list of lexeme sets paired with correct surface forms, and frequencies '''
	def __init__(self,filename):
		self.lexicon = {} # dictionary of {tag: lexeme}
		self.learnData = [] # each entry is a list: [lexemes,surface].  lexemes is itself a list, of all lexemes involved in the entry
		self.sampler = [] # summed to 1, sampler for each learnData entry
		                  # derived from either obs.prob, or tab.prob*obs.prob, if tab.prob is present

		self.noisy = True # If true, will print out lots of junk as it reads in
		self.tableaux = [] # If candidates appear in the input file, this will contain tableaux, otherwise it will be empty
		self.tabProb = [] # a separate sampler for tableaux specifically, for use in simple tableau-based learning.
		self.tableauxTags = [] # tag of each tableau.  Should correspond to the 'input' column in the data
		self.constraintNames = [] # If columns appear after all the pre-determined column types, they will be interpreted as constraints

		# What kind of input file is this
		candidates = False
		hidden = False
		freq_weighted = False
		specialLex = False

		f = open(filename, "r")
		lines = f.readlines()
		header = lines[0].split('\t')
		header = [label.strip() for label in header]
		constraintsStartAt = 0 # At which column do the constraint names start
		if 'input' in header:
			iIndex = header.index('input')
			constraintsStartAt += 1
		else:
			print("ERROR: No column of your input file is labeled 'input'.  This column is required, and must be labelled exactly.  Please check your input file and try again")
			sys.exit()

		if 'obs.prob' in header:
			oIndex = header.index('obs.prob')
			constraintsStartAt += 1
		else:
			print("ERROR: No column of your input file is labeled 'obs.prob'.  This column is required, and must be labelled exactly.  Please check your input file and try again")
			sys.exit()
		if 'candidate' in header:
			candidates = True
			cIndex = header.index('candidate')
			constraintsStartAt += 1
			if self.noisy:
				print("Your input file contains candidates, therefore candidates will not be generated for you.")
		if 'surface' in header:
			hidden = True  # Its always going to be hidden, right? cause if there are no candidates then the tableau generation system will generate hidden structure
			sIndex = header.index('surface')
			constraintsStartAt += 1
			if self.noisy:
				print("Your input file contains hidden structure!  Yay!  I'll try to fit that with Expectation-Maximization according to Jarosz (2013)")
				#TODO create more nuanced printout for lexeme files
		if 'tab.prob' in header:
			freq_weighted = True
			tpIndex = header.index('tab.prob')
			constraintsStartAt += 1
			if self.noisy:
				print("Your input file contains input frequency information (it's the column labelled, somewhat opaquely, 'tab.prob')  Learning will therefore proceed according to this frequency-weighting. \n Note that you can turn off frequency weighting by... ") # TODO include note about how to turn off frequency weighting
		if 'lexeme' in header:
			specialLex = True
			lIndex = header.index('lexeme')
			constraintsStartAt += 1
			if self.noisy:
				print("Your input file contains specially defined lexemes.  I'll use lexeme names from the 'input' column, but lexeme phonemes from the 'lexeme' column.")

		if len(header)> constraintsStartAt:
			self.constraintNames=header[constraintsStartAt:]

		inpt_s = []
		for i in lines[1:]:
			l = [j.strip() for j in i.split('\t')]
			inpt = l[iIndex]

			# Add lexemes
			lex = inpt.split("_")
			if specialLex:
				splex = l[lIndex].split("_")
				parsed = []
				for sp in splex:    #faqa_alo-f-ia
					split = sp.split('-')
					for m in range(0,len(split)):
						if m%2:
							prev = parsed[-1] # [segments, activities]
							segments = prev[0]+split[m] # 'alof'    'faqaf'   'falof'
							act = prev[1]+[0 for c in split[m]] # [1,1,1,0]    [0,1,1,1,0]
							parsed.append([segments,act])
						elif m>1: #greater than 1 and NOT even - entry before was liason
							segments = split[m-1]+split[m]   # 'fia'    'falo'
							act = [1 for c in split[m-1]]+[0 for c in split[m]] # [0,1,1]  [0,1,1,1]
							parsed.append([segments,act])
						else: #m=0, the first thing
							segments = split[m]
							act = [1 for c in split[m]]
							parsed.append([segments,act])
				if len(parsed) != len(lex):
					continue
					#TODO functionality for if the input has a LOT of ambiguous material '-asdhjk-' split over multiple morphemes
				splex = parsed

			else:
				splex = lex

			lexList = [] #to be filled with lexeme objects
			for item,sp in zip(lex,splex):
				if item not in self.lexicon:  # changed lexicon to a dictionary
					if specialLex:
						self.lexicon[item] = lexeme(item,[character for character in sp[0]])
						self.lexicon[item].activitys = sp[1]
					else:
						self.lexicon[item] = lexeme(item,[character for character in sp])

				lexList.append(self.lexicon[item])


			if inpt not in inpt_s: #If we haven't seen this input before
				inpt_s.append(inpt)
				if candidates:
					if freq_weighted:
						p = l[tpIndex]
					else:
						p=1

					self.tabProb.append(p)  #Note that only the first tab.prob value in a tableau with many candidates will be recorded.
					self.tableaux.append(Tableau(inpt,p,hidden,lexemes = lexList))
					self.tableaux[-1].constraintNames = self.constraintNames # Assign each tableau the constraint names from the input file
					self.tableauxTags.append(self.tableaux[-1].tag)
					# create a new Tableau object for a unique input


			if candidates: # If there are candidates, populate the tableaux
				c = l[cIndex]
				s = l[sIndex] if hidden else c # surface form, defaults to candidate form if no hidden struct
				v = [float(viol) for viol in l[constraintsStartAt:]] # Note that this could be empty
				self.tableaux[-1].addCandidate(candidate(c,v,l[oIndex],s))



			#TODO check
			#self.learnData.append([lexList,l[sIndex]])# This line is meant to represent *correct* output
			# There are two ways this can go:
			# 1) they give a simple input file, with each observed output on a separate line, with obs.prob indicating how often that appears
			# 2) they give an input file with whole tableaux in it, so need to calculate which are the observed outputs (which have any probability)

			# ok wait this is easier than I think
			if hidden:
				self.learnData.append([lexList,l[sIndex],inpt])
			elif candidates:
				self.learnData.append([lexList,l[cIndex],inpt])
			else:
				print("ERROR: no column with surface forms in it.  Please add either a 'candidate' column, or a 'surface' column")
				sys.exit()
			if freq_weighted:
				self.sampler.append(float(l[tpIndex])*float(l[oIndex]))
			else:
				self.sampler.append(float(l[oIndex]))

		self.sampler = [s/sum(self.sampler) for s in self.sampler] # convert to a well-formed distribution
		# TODO do I have to worry about these getting too small


	def __str__(self):
		trainTags = []
		for i, k in zip(self.learnData,self.sampler):
			entry = []
			for j in i[0]:
				entry.append(j.tag)
			entry =["+".join(entry)]
			entry.append(i[1])
			entry.append(str(round(k,4)))
			trainTags.append(entry)

		maxLen_lex = str(max([len(i[0]) for i in trainTags]+[7])+1)
		maxLen_out = str(max([len(i[1]) for i in trainTags]+[7])+1)
		segform = ('{:' + maxLen_lex + 's} ') + ('{:' + maxLen_out + 's} ') + ('{:8}')

		out = "Training Data: "
		out += '\n'
		out += segform.format("lexemes","surface","training probability")
		for i in trainTags:
			out += '\n'
			out += segform.format(*i)

		return out

	def decayLexemes(self):
		for lex in self.lexicon:
			self.lexicon[lex]





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
		if len(lexemes)>1:
			faiths = list(itertools.product(individualCands[0],individualCands[1]))
		else:
			faiths = individualCands
		# TODO This is where it's limited to two lexemes only

	#TODO implement scramble option

	# concatenate richCands
	fcs = [] #'fc' = 'faithful candidate'
	containsObsOut = 0
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
		containsObsOut = 1 if newC==obsOutput else 0

		fcs.append(richCand(newC,[],obsProb,newSegsDict,newSegsList,None,newActivitys,newSuprasegmentals,surfaceForm=newC))


	#Assign markedness violations to faithful candidates
	cs = [c.c for c in fcs]
	for fc in fcs:
		for con in constraints:
			fc.violations.append(con.assignViolations(fc,featureSet))

	allCands = fcs
	#for c in allCands:
	#	print(c)

	# Generate new candidates, dropping off at a rate controlled by A as you get farther down the 'tree' and rejecting them if they are not harmonically improving, according to s
	moarCandidates = 1
	t = 1  # 'time', or the depth in the tree
	A = 10 # higher -> more candidates (keep traversing the tree)
	s = 20 # sigmoid parameter  higher--> more candidates
	while moarCandidates:
		for o in operations:
			for c in allCands:
				# apply o with probability A/t
				if random.random()<A/t or not(containsObsOut): #Continue to generate candidates until you generate the observed output
					try:
						candidates = o(c,featureSet)
					except:
						print("Error, trying to apply operation  to candidate ", c)
					if type(candidates)==tuple:
						candidates, *_ = candidates
					#print(candidates)
					candidates = [can for can in candidates if can.c not in cs]
					# TODO check operations list also to establish sameness
					for possibleCand in candidates:
						for con in constraints:
							#print('1')
							#	print(con.name)
							possibleCand.violations.append(con.assignViolations(possibleCand,featureSet))
							#	print("violations: ",possibleCand.c)
							#	print(possibleCand.violations)

					#for possibleCand in candidates:
					#	print(possibleCand.violations)

						if possibleCand.surfaceForm == obsOutput:
							containsObsOut=1
							possibleCand.observedProb=1
							allCands.append(possibleCand)
							cs.append(possibleCand.c)
						else:
							possibleCand.harmony = -sum(viol*weight for viol,weight in zip(possibleCand.violations,w))
							Hdiff = possibleCand.harmony - c.harmony
							p_keep = (1/2)*Hdiff/math.sqrt(s+Hdiff**2)+0.5 # Here is the equation for keeping a candidate based on harmony
							if random.random()<p_keep:
								possibleCand.observedProb = 1 if possibleCand.surfaceForm==obsOutput else 0
								allCands.append(possibleCand)
								cs.append(possibleCand.c)



		t+=1
		if random.random()<(1-(A/t))**(len(operations)) or not(containsObsOut):
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
				constraintList.append((pfc.name,pfc))
				w.append(pfc.w)
		wNum+=1

	tab = Tableau("_".join([l.tag for l in lexemes]))
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



		#last_match_col = 0  # column of last match on this row

		for col in range(1, len(cdiff.segsList)+1):
			seg_diff = [f for f in cdiff.segsDict[cdiff.segsList[col-1]] if f[0]!=skipChar]

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
			if ch != 'EPEN':
				# feature_on_segment
				listOfPFCs.append((10,f,seg))
				#TODO 10 is the initial weight of PFC's - a parameter of learning

				# feature exists
				listOfPFCs.append((10,f))

	nPFCs = np.random.poisson(lamb,1)[0]
	nPFCs = len(listOfPFCs) if len(listOfPFCs)<= nPFCs else nPFCs
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
