#Max

#Dep

#Uniformity

#Onset
import learner as l


def Max(rC,features):
	candidates,activitys = delete(rC,features)
	for c,a in candidates,activitys:
		c.violations.append(a)
	return candidates

def Uniformity(rC,features):
	candidates = merge_same(rC,features)
	for c in candidates:
		c.violations.append(1)
	return(candidates)

def NoCoda(rC,featureSet):
	'''This will only work for no onset cluster languages!'''
	#Essentially, a C has to be covered by a V
	coda = 0
	consonantLast = 0
	for i in rC.segsList:
		if ('0','syllabic') in rC.segsDict[i]:
			if consonantLast == 1:
				coda +=1
			consonantLast = 1
		else:
			consonantLast =0
	return coda

def Hiatus(rC,featureSet):
	hiatus = 0
	vowelLast = 0
	for i in rC.segsList:
		if ('1','syllabic') in rC.segsDict[i]:
			if vowelLast == 1:
				hiatus +=1
			vowelLast = 1
		else:
			vowelLast = 0
	return hiatus
	
constraints = [NoCoda,Hiatus]	

# testing script:
#Uniformity(l.exlex_ami().toRichCand(l.Features('features.txt'))[0],l.Features('features.txt'))

#delete(l.exlex_ami().toRichCand(l.Features('features.txt'))[0],l.Features('features.txt'))
#a =morphFeature(l.exlex_ami().toRichCand(feat)[0],feat,'voice')




def morphFeature(rC,features,featureName,values = ['1','0']):
	candidates = []
	for s in rC.segsList:
		# go through each segment
		# check if changing featureName results in another entry in features
		# If so, add it to candidates
		fs = [[str(i) for i,j in rC.segsDict[s]],[str(j) for i,j in rC.segsDict[s]]]
		featureValue = fs[0][fs[1].index(featureName)]
		for v in values:
			if v !=featureValue:
				fs[0][fs[1].index(featureName)] = v
				newSegs = ([i for i in zip(fs[0],fs[1])])
				seg = features.exists(newSegs)
				if seg: # if morphing the feature leads to something that exists, add the new candidate
					newSegsDict = rC.segsDict.copy()
					newSegsDict[s] = newSegs
					newC = features.featureToS(newSegsDict,rC.segsList[:])
					#assuming that segsList is in the correct order
					newC = [q for q in newC]
					newC.insert(rC.segsList.index(s)+1,'(f)')
					newC = ''.join(newC)
					candidates.append(l.richCand(newC,rC.violations[:],rC.observedProb,newSegsDict,rC.segsList[:],rC.segsOrder[:],rC.activitys[:],rC.suprasegmentals,surfaceForm=None))
	
	return candidates
		

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
		#Assuming that segsList is in the correct order (such that rC.segsOrder is redundant)
		newC = [q for q in newC]
		newC.insert(i,'(_)')
		newC = ''.join(newC)
		candidates.append(l.richCand(newC,rC.violations[:],rC.observedProb,newSegsDict,newSegsList,newSegsOrder,newActivitys,rC.suprasegmentals,surfaceForm=None))
		activitys.append(activity)
		
	return(candidates,activitys)
	

def merge_same(rC,features):
	# This function assumes that rC.segsList is in the same order as rC.segsOrder (they are essentially redundant)
	candidates = []
	for i in range(0,max(rC.segsOrder)):  # iterate from 0 to the largest number in segsOrder
		# get adjacent segments at this location
		# First, get all indices of segsOrder where the value is i
		#Note that the usage of toRichCand() will prevent multiple segments occurring in the same slot in the order
		indices = [x for x in range(len(rC.segsOrder)) if rC.segsOrder[x] == i]
		# Then, get the indices for the next highest value (they might not be adjacent!)
		indices_plus1 = [x for x in range(len(rC.segsOrder)) if rC.segsOrder[x] ==min([k for k in rC.segsOrder if k>i]+[10000000000])]
		
		#print(indices)
		#print(indices_plus1)
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
					#print(newSegsDict)
					#print(newSegsList)
					newC = features.featureToS(newSegsDict,newSegsList)
					newC = [q for q in newC]
					newC.insert(s,'(m)')
					newC = ''.join(newC)
					candidates.append(l.richCand(newC,rC.violations[:],rC.observedProb,newSegsDict,newSegsList,newSegsOrder,newActivitys,rC.suprasegmentals,surfaceForm=None))
	return((candidates))


operations = [delete, merge_same]