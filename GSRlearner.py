# import things that need to be imported here
from pandas import read_excel
import numpy as np 
import math
import Constraints
import re

#####################################################


class lexeme:
	def __init__(self, tag, allomorphs, kind):
		self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
		self.allomorphs = allomorphs # list of allomorphs, in the following format:

# allomorph lists for roots only have one entry
# w/ C
# [[ 'tagis', 0.4]]    <-- number is activity level of thematic C.  We will assume that thematic C's are firs in suffixes, last in roots
# w/o C
# [[ 'apa',  0.0]]
#
# Affixes may have more than one entry
# [[ 'sia',  0.3],
#  [ 'mia', 0.2],
#  [ 'fia',  0.3],
#  [ 'tia', 0.6],
# ...
#  [ 'ina', 0.0],
#  [ 'a', 0.0]
# ]

		self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc.
		self.freq = 0   #initialize at zero, increase during learning
		

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
	
	def sample(self, n):
		# sample 
		#break
		return 0
			
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
		
		
# hard-coding suffixes for now

#		for x in range(len(suffix)):  # looping through suffixes column
#			suff_sets = [['ia','a','ina'],['aga','ga']]
#			allomorphs = []
#			if x in ['i','ia','aga','aqi']:  # could adjust this later to try C's on every form - would need to add *CC
#				for y in them_c:  # concat each suffix with all possible them_c
#					allomorphs.append([y+suffix[x]]+[0])
#			for suff in suff_sets:
#				if x in suff:
#					for y in suff:
#						if y != x:
#							allomorphs.append(y)
#			
#			self.add_lexeme(lexeme(suffix[x], allomorphs, 'suffix'))
   
   
   
  
class Tableau: 
	def __init__(self,inpt,prob=1):
		self.inpt = inpt # text specifying the input.  

		self.candidates = [] # To be filled during tableau creation

		self.probDenom = 1 # denominator for calculating MaxEnt prob of each candidate
						   # this is the sum of each exponentiated harmony score
		self.predProbsList = [] # list of each candidate's predicted probability; used in sampling
								# gets filled (and updated) during learning
		self.obsProbsList = [] 	# list of each candidate's observed probability; used in sampling


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

	def addCandidate(self,cand):
		self.candidates.append(cand)
		self.obsProbsList.append(cand.observedProb)

			
	def checkViolationLength(self): 
		'''check if all the violation vectors are the same length'''
		l = len(self.candidates[0])
		for i in range(0,len(self.candidates)):
			if len(i.violations) != l:
				print("Not all violation vectors are the same length!\n", "Candidate ",i.c, "has ", len(i.violations), ", while the previous candidate has ", l, " violations.")
				return 0
			else:
				return 1

	def calculateHarmony(self, w): 
		'''Takes a vector of weights, equal in length to the violation vectors of the candidates.  Populates the harmony parameter of each candidate based on the weight vector w'''
		# Requires t, decayRate, and decayType if decay is active in learning.  First step in calculating harmony is to make sure you do it with updated PFC weights
		# suppressPFC is used in case you would normally calculate harmony with PFCs but you want to ignore the PFC weights just this time (like, to predict the harmonies if this LexEntry were really a nonword)

		self.probDenom=0 # Reset probDenom.  Even though this function is dedicated to calculating the harmony, it's still useful to take this opportunity to calculate the MaxEnt denominator.  If you're managing to use this program to do Noisy HG or something, this will be meaningless.
		
		for cand in self.candidates:
			# Calculate that good 'ole dot product!
			cand.harmony = sum(viol*weight for viol,weight in zip(cand.violations,w))
			# Assuming the candidate's violations and weights are the correct sign, this dot product will be a negative number

			try:
				self.probDenom += pow(math.e,cand.harmony)
			except OverflowError:
				print("Something's wrong with the exponentiation in calculating the MaxEnt denominator.  Python's patience with giant exponents only stretches so far...")
				print(self.inpt)
				print(cand)
				print(cand.harmony)
				print(w)	


	def predictProbs(self,w):
		'''Convert harmony scores, and the MaxEnt denominator, to predicted probabilities for each candidate output in the Tableau '''
		self.calculateHarmony(w) # start by getting those harmonies
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
				print(self.ur)
				print(cand.c)
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

		error = (0 if obs==pred else 1)

		return error, obsCandidate, predCandidate
		
		
  
class candidate: 
	def __init__(self,c,violations,observedProb,activityLevel,surfaceForm=None):
		self.c = c # the actual candidate 
		self.surfaceForm = surfaceForm
		self.violations = violations # list of violations, in same order as constraints
		self.observedProb = observedProb # The observed probability of the candidate
		try: # make sure observedProb is a float, or can be converted to float
			self.observedProb = float(self.observedProb)
		except ValueError:
			print("It looks like your candidates' probabilities can't all be converted to floats.  Check if there's some text in that column")
		self.harmony = 0 # Not specified at initialization.	 This will be filled out in learning
		self.predictedProb = 0 # Again, to be filled out during learning.
#		self.checkViolationsSign() # On initialization, make sure all violations are negative
		self.activityLevel = activityLevel # float of activity level of thematic C of the candidate for calculating violations
	
	def applyConstraints(self, constraints=Constraints.con):
		self.violations=[i(self) for i in constraints]
		# TO DO: append, or overwrite?



class Grammar:
	def __init__(self,file_name,sheet_number=1):
		self.learningData = self.readLearningData(file_name,sheet_number)  # An array or something containing the learning data
		self.constraints = Constraints.conNames # Read these off the top of the input data file.
		self.w = [] # Weights, starts empty
		self.initializeWeights() # Initialize weights when Tableaux object is created (to zero, or some other vector depending on how you call this function.)
		self.t = 0	# For learning, t starts at 0
		self.learningRate = 0.1
		self.activityUpdateRate = 0.05
		# self.lexicon also exists - created with readLearningData


	def readLearningData(self,file_name,sheet_number=1):
		self.lexicon=Lexicon(file_name,sheet_number)
		input_dt_frame = read_excel(file_name, sheet_number-1 ) #this is for the sheet#1;
		input_np = input_dt_frame.to_numpy()
		
		return input_np
	
	
	def createLearningPlaylist(self,n):
		# n is total number of learning simulations
		#First, create list of inputs, with frequencies
		observeds = []
		freqs = []
		base_tags = []
		suff_tags = []
		
		for i in self.learningData:
			observeds.append(i[1])
			freqs.append(i[5])
			if i[5]=='nan':
				print(i)
			base_tags.append(i[6])
			suff_tags.append(i[4])

		
		playlist_nums = list(np.random.choice(range(0,len(observeds)),n,p=[(i+1)/(sum(freqs)+len(freqs)) for i in freqs]))
		playlist = []
		for i in playlist_nums:
			playlist.append([observeds[i],self.lexicon.lexemeList[base_tags[i]],self.lexicon.lexemeList[suff_tags[i]]])
		
		return playlist



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
			


	def update(self,datum): # datum is an entry from playlist
		# Start with a learning datum
		# Create a tableau
		tab = Tableau(datum[0])
		tab.candidates = tab.generate_candidates(datum[1],datum[2],datum[0])
		for cand in tab.candidates:
			try:
				cand.applyConstraints()
			except:
				print(cand)
				print(datum)
				print(datum[1].allomorphs)
				print(datum[2].allomorphs)
			print(cand.c,cand.surfaceForm,cand.observedProb,cand.violations)
		# Generate a prediction
		e, obs, pred = tab.compareObsPred(self.w)
		print(e,obs.c,pred.c,obs.violations,pred.violations)
		if e:
			#update general weight: perceptron update
			self.w = [wt+(p-o)*self.learningRate for wt,p,o in zip(self.w,pred.violations,obs.violations) ]
			
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
		return e
		
	
	def epoch(self,playlist,niter,start=0):
		errors = 0
		for i in range(0,niter):
			errors+=self.update(playlist[start+i])
			print(start+i)
			
		error_rate = errors/niter
		return error_rate
		
		
		
	def learn(self,nIterations,nEpochs):
		
		playlist = self.createLearningPlaylist(nIterations*nEpochs)
		for i in range(0,nEpochs):
			self.epoch(playlist,nIterations,start=nIterations*i)

	



#testing for read_input and sampling  

#read input and initialize the grammar object
#new_grammar = Grammar(read_input("learning_input.xlsx", 0))
#test sample function using the learniing data from grammar object
#new_sample = new_grammar.sample(1000,new_grammar.learningData)
#print(new_sample)
#new_lexicon.check_sample(new_sample,new_grammar.learningData)
#print (new_grammar.learningData)





	


		
		
 
