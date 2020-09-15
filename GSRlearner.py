# import things that need to be imported here

#####################################################


class lexeme:
    def __init__(self, tag, allomorphs, kind):
        self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
        self.allomorphs = allomorphs # list of allomorphs, in the following format:

# [[ 'string', 1],    <-- number is activity level of thematic C.  We will assume that thematic C's are firs in suffixes, last in roots
#  [ 'tagis',  0.7],        
#  [ 'tagi',   0.0],
#  ...
# ]]

# [[ 'ia',  0.0],
#  [ 'ina', 0.0],
#  [ 'a',  0.0],
#  [ 'sia', 0.4],
# ...
# ]]

        self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc.
        self.freq = 0   #initialize at zero, increase during learning
        


class Lexicon:
    def __init__(self):
        self.lexemeList = []  #initialise empty list for storing lexemes in
        self.freqList = []    #empty list for storing each lexeme's frequency - used for sampling
        
        
    def add_lexeme(self,l):
        # Add a lexeme to the lexemeList
        self.lexemeList(l)
        self.freqList.append(l.freq)
        
    
    def update_freqList(self):
        # update freqList with all lexemes' frequencies, in case they have changed
        self.freqList = []
        for l in self.lexemeList:
            self.freqList.append(l.freq)


    def sample(self, n):  # sample 
        break
        

        
  
class Tableau: 
	def __init__(self,inpt,prob=1,pfc=None):
		self.inpt = inpt # text specifying the input.  

		self.candidates = [] # To be filled during tableau creation

		self.probDenom = 1 # denominator for calculating MaxEnt prob of each candidate
						   # this is the sum of each exponentiated harmony score
		self.predProbsList = [] # list of each candidate's predicted probability; used in sampling
								# gets filled (and updated) during learning
		self.obsProbsList = [] 	# list of each candidate's observed probability; used in sampling


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

	def getObsWinner(self):

		# Get candidate list
		# Get probability list
		winCandidate = self.candidates[np.random.choice(range(0,len(self.candidates)),1,p=self.obsProbsList)[0]]
		winner = winCandidate.c
		return winner, winCandidate

	def compareObsPred(self,w):
		self.predictProbs(w)
		pred, predCandidate=self.getPredWinner() # Sample from predicted distribution
		obs, obsCandidate=self.getObsWinner() # Sample from observed distribution

		error = (0 if obs==pred else 1)

		return error, obsCandidate, predCandidate
        
        
  
class candidate: 
	def __init__(self,c,violations,observedProb,surfaceForm=None):
		self.c = c # the actual candidate 
		self.violations = violations # list of violations, in same order as constraints
		self.observedProb = observedProb # The observed probability of the candidate
		try: # make sure observedProb is a float, or can be converted to float
			self.observedProb = float(self.observedProb)
		except ValueError:
			print("It looks like your candidates' probabilities can't all be converted to floats.  Check if there's some text in that column")
		self.harmony = 0 # Not specified at initialization.	 This will be filled out in learning
		self.predictedProb = 0 # Again, to be filled out during learning.
		self.checkViolationsSign() # On initialization, make sure all violations are negative




class Grammar:
    def __init__(self,learningData):
        self.learningData = learningData  # An array or something containing the learning data
        self.constraints = [] # Read these off the top of the input data file.
        self.w = [] # Weights, starts empty
        self.initializeWeights() # Initialize weights when Tableaux object is created (to zero, or some other vector depending on how you call this function.)
        self.t = 0	# For learning, t starts at 0
        self.lexicon = Lexicon()  # Starting with an empty lexicon; can change later if we want
        self.learningRate = 0.1
        self.activityUpdateRate = 0.05


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




	def update(self):
        
        
    def learn(self):
    
    def epoch(self):
