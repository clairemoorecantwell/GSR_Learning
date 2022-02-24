import learner as l
import re

class constraint:
	def __init__(self,name,func = lambda x:0,MF='M',operation=None):
		self.name = name
		self.assignViolations = func
		self.MF = MF
		self.operation = operation # This one is the operation for creating candidates, expected for faithfulness constraints




def Ident_back_IO(input,output,features):
	'''compares an input and output string, no need to define an operation'''
	violations = 0
	blih, blah, blug, backtrace = l.diffCands(input.toRichCand(features),output.toRichCand(features))
	for change in backtrace: # each entry of backtrace is a tuple ("CHANGE",[]), ("DEL",[]) etc, where the list is features different (either changed or added)
		for feature in change[1]:
			if feature[1]=='back':
				violations += 1
	return violations


def ABN(output,features):
	''' Assign a violation to every front vowel preceded by a back vowel'''
	# regardless of rounding.  Note that this seems to differ from hayes et al, pg.836, table 3
	violations = 0
	rC = output.toRichCand(features)
	existsBack = False
	for s in rC.segsList:
		if ("1","back") in rC.segsDict[s]:
			existsBack = True
		if ("0","back") in rC.segsDict[s] and existsBack:
			violations+=1
			print(s)
	return violations

def AFL(output,features):
	''' Assign a violation to every back vowel immediately preceded by a front vowel'''
	# regardless of rounding.  Note that this seems to differ from hayes et al, pg.836, table 3
	violations = 0
	rC = output.toRichCand(features)
	existsFront = False
	for s in rC.segsList:
		if existsFront: # you've just seen a front vowel
			if ("1","back") in rC.segsDict[s]:
				violations += 1
				existsFront = False
		if ("0","back") in rC.segsDict[s]:
			existsFront = True

	return violations

def AFNL(output,features):
	''' Assign a violation to every back vowel immediately preceded by a nonlow front vowel'''
	# regardless of rounding.  Note that this seems to differ from hayes et al, pg.836, table 3
	violations = 0
	rC = output.toRichCand(features)
	existsFront = False
	for s in rC.segsList:
		if existsFront: # you've just seen a front vowel
			if ("1","back") in rC.segsDict[s]:
				violations += 1
				existsFront = False
		if ("0","back") in rC.segsDict[s] and ("0","low") in rC.segsDict[s]:
			existsFront = True

	return violations


def AFLL(output,features):
	''' Assign a violation to every back vowel immediately preceded by a low front vowel'''
	# regardless of rounding.  Note that this seems to differ from hayes et al, pg.836, table 3
	violations = 0
	rC = output.toRichCand(features)
	existsFront = False
	for s in rC.segsList:
		if existsFront: # you've just seen a front vowel
			if ("1","back") in rC.segsDict[s]:
				violations += 1
				existsFront = False
		if ("0","back") in rC.segsDict[s] and ("1","low") in rC.segsDict[s]:
			existsFront = True

	return violations


Id_back = constraint("Ident-back",Ident_back_IO,MF="F")
Agree_back_nonlocal = constraint("Agree_back_nonlocal",ABN)
Agree_front_local = constraint("Agree_front_local",AFL)
Agree_front_nonlow_local = constraint("Agree_front_nonlow_local",AFNL)
Agree_front_low_local = constraint("Agree_front_low_local",AFLL)

constraints = [Id_back,Agree_front_local,Agree_back_nonlocal,Agree_front_low_local,Agree_front_nonlow_local]
