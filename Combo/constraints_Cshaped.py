import learner as l
import re

class constraint:
	def __init__(self,name,func = lambda x:0,MF='M',operation=None):
		self.name = name
		self.assignViolations = func
		self.MF = MF
		self.operation = operation # This one is the operation for creating candidates, expected for faithfulness constraints

def ident(UR,SR):
    '''compares an input and output string, no need to define an operation'''
    violations = 0
    if UR!=re.sub("_","",SR.c):
        violations+=1
    #print(UR)
    #print(SR.c)
    return violations

Ident = constraint("Ident",ident,MF='F')


constraints = [Ident]
