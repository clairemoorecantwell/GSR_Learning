#Max

#Dep

#Uniformity

#Onset


def Max(rC,features):
	candidates= []
	for i in range(0,len(rC.segsList)):
		newSegsList = rC.segsList[:i]+rC.segsList[i+1:]
		newSegsDict = rC.segsDict.copy()
		newSegsOrder = rC.segsOrder[:i]+rC.segsOrder[i+1:]
		newActivitys = rC.activitys[:i]+rC.activitys[i+1:]
		activity = rC.activitys[i]
		newC = features.featureToS(newSegsDict,newSegsList)
		candidates.append(l.richCand(newC,rC.violations[:]+[activity],rC.observedProb,newSegsDict,newSegsList,newSegsOrder,newActivitys,rC.suprasegmentals,surfaceForm=None))
	
	return candidates

def Uniformity(rC,features):
	candidates=[]
	for i in range(0,max(rC.segsOrder)):  # iterate from 0 to the largest number in segsOrder
		# get adjacent segments at this location
		# First, get all indices of segsOrder where the value is i
		 indices = [x for x in range(len(rC.segsOrder)) if rC.segsOrder[x] == i]
		#First, do they match totally?
		if rC.segsDict[rC.segsList[i]] == rC.segsDict[rC.segsList[i+1]]:
			# add a candidate with a simple uniformity violation
			newSegsList = rC.segsList[:i+1]+rC.segsList[i+2:]
			newSegsDict = rC.segsDict.copy()
			newSegsDict.pop(newSegsList[i+1])
			
	
	
	
	
	
	
	def __init__(self,c,violations,observedProb,segsDict,segsList,segsOrder=None,activitys=None,suprasegmentals = None,surfaceForm=None):
		candidate.__init__(self,c,violations,observedProb,surfaceForm)
		self.segsDict = segsDict # This should be a dictionary with keys for segments, and values that are lists of tuples defining the features of each seg.
		# Example: {seg1: [(0, "front"),(1, "high"),(0,"back"),(0,"low")]}
		self.segsList = segsList # list of all segments
		self.segsOrder = segsOrder if segsOrder else [i for i in range(1,len(segsList)+1)]
		# set segsOrder to the order of the segments in segsList if a particular order is not specified
		self.activitys = activitys if activitys else [1 for i in segsList] # set all activitys to 1 by default
		self.suprasegmentals = suprasegmentals
