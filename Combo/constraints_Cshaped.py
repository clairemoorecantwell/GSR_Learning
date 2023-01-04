import learner as l
import re

class constraint:
	def __init__(self,name,func = lambda x:0,MF='M',operation=None):
		self.name = name
		self.assignViolations = func
		self.MF = MF
		self.operation = operation # This one is the operation for creating candidates, expected for faithfulness constraints

	def isLexicalizable(self):
		# TODO check whether the constraint returns the right shape:
		# (vSum, vs, indices)
		return True


def ident(UR,SR):
	'''compares an input and output string, no need to define an operation'''
	vSum = 0
	vs = []
	indices = []

	parsedUR = UR.split("_")
	parsedSR = SR.split("_")
	if len(parsedSR) != len(parsedUR):
		parsedUR = [re.sub("_","",UR)]
		parsedSR = [re.sub("_","",SR)]
		
	startIndex = 0
	for ur, sr in zip(parsedUR,parsedSR):

		if ur!=sr:
			vSum += 1
			vs.append(1)
			endIndex = startIndex + len(sr)-1
			indices.append((startIndex,endIndex))

		startIndex += len(sr)+1

	return (vSum, vs, indices)

Ident = constraint("Ident",ident,MF='F')


def syncope(SR):
    indices = []
    vs = []
    vSum = 0
    for m in re.finditer('(?=([pnytlmkhwS]_?[ieau]_?[pnytlmkhwS]))',SR):
        start = m.start(0)
        end = start + len(m.group(1))-1
        indices.append((start,end))
        vs.append(1)
        vSum += 1

    return (vSum, vs, indices)

Syncope = constraint("Syncope",syncope,MF='M')

#beA
#beB


constraints = [Ident,Syncope]
