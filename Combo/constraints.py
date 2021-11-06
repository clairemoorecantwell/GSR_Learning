#Max

#Dep

#Uniformity

#Onset


def Max(rC,features):
	candidates,activitys = delete(rC,features)
	for c,a in candidates,activitys:
		c.violations.append(a)
	return candidates

def Uniformity(rC,features):
	candidates=[]
	for i in range(0,max(rC.segsOrder)):  # iterate from 0 to the largest number in segsOrder
		# get adjacent segments at this location
		# First, get all indices of segsOrder where the value is i
		#Note that the usage of toRichCand() will prevent multiple segments occurring in the same slot in the order
		indices = [x for x in range(len(rC.segsOrder)) if rC.segsOrder[x] == i]
		# Then, get the indices for the next highest value (they might not be adjacent!)
		indices_plus1 = [x for x in range(len(rC.segsOrder)) if rC.segsOrder[x] ==min([k for k in rC.segsOrder if k>i]+[10000000000])]
		
		print(indices)
		print(indices_plus1)
		for f in indices:
			for s in indices_plus1:
				#First, do they match totally?
				if rC.segsDict[rC.segsList[f]] == rC.segsDict[rC.segsList[s]]:
					# add a candidate with a simple uniformity violation
					newSegsList = rC.segsList[:]
					newSegsList.pop(s) #just delete the second thing
					newSegsOrder = rC.segsOrder[:]
					newSegsOrder.pop(s)
					newActivitys = rC.activitys[:]
					newActivitys.pop(s)
					newSegsDict = rC.segsDict.copy()
					newSegsDict.pop(rC.segsList[s])
					print(newSegsDict)
					print(newSegsList)
					newC = features.featureToS(newSegsDict,newSegsList)
					newC = [q for q in newC]
					newC.insert(s,'(m)')
					newC = ''.join(newC)
					candidates.append(l.richCand(newC,rC.violations[:]+[1],rC.observedProb,newSegsDict,newSegsList,newSegsOrder,newActivitys,rC.suprasegmentals,surfaceForm=None))
	return(candidates)
	

# testing script:
Uniformity(l.exlex_ami().toRichCand(l.Features('features.txt'))[0],l.Features('features.txt'))

delete(l.exlex_ami().toRichCand(l.Features('features.txt'))[0],l.Features('features.txt'))




# Operations list
def delete(rC,features):
	candidates = []
	activitys = []
	for i in range(0,len(rC.segsList)):
		newSegsList = rC.segsList[:i]+rC.segsList[i+1:]
		newSegsDict = rC.segsDict.copy()
		newSegsOrder = rC.segsOrder[:i]+rC.segsOrder[i+1:]
		newActivitys = rC.activitys[:i]+rC.activitys[i+1:]
		activity = rC.activitys[i]
		newC = features.featureToS(newSegsDict,newSegsList)
		newC = [q for q in newC]
		newC.insert(i,'(_)')
		newC = ''.join(newC)
		candidates.append(l.richCand(newC,rC.violations[:],rC.observedProb,newSegsDict,newSegsList,newSegsOrder,newActivitys,rC.suprasegmentals,surfaceForm=None))
		activitys.append(activity)
		
	return(candidates,activitys)
	






	
	
	
	
	def __init__(self,c,violations,observedProb,segsDict,segsList,segsOrder=None,activitys=None,suprasegmentals = None,surfaceForm=None):
		candidate.__init__(self,c,violations,observedProb,surfaceForm)
		self.segsDict = segsDict # This should be a dictionary with keys for segments, and values that are lists of tuples defining the features of each seg.
		# Example: {seg1: [(0, "front"),(1, "high"),(0,"back"),(0,"low")]}
		self.segsList = segsList # list of all segments
		self.segsOrder = segsOrder if segsOrder else [i for i in range(1,len(segsList)+1)]
		# set segsOrder to the order of the segments in segsList if a particular order is not specified
		self.activitys = activitys if activitys else [1 for i in segsList] # set all activitys to 1 by default
		self.suprasegmentals = suprasegmentals
