# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 21:51:08 2020

@author: richa
"""


##############
# evaluate candidates by DEP constraint and assign violations
##############

#Function: evaluate candidates by DEP constraint and assign violations

#Input: one candidate object (defined in the candidate class)
#Output: violation points

from GenerateCandidate_function import generate_candidate
import GSRlearner as gsrln

def DEP(cand):
    if cand.activityLevel > 1 or cand.activityLevel == 0: #if the candidate's activity level is greater than 1 or equals to 0, returns 0
        return 0
    else: # otherwise subtract the activity level from 1 and return
        return 1-cand.activityLevel
    
#Test data(from Angela's GenerateCandidate_function.py file)
#=============================================================================
rt2 = [['tagis', 0.4]]
rt_lex = gsrln.lexeme('tagi', rt2, 'root')

sf2 = [['ina', 0.3], ['a', 0.3], ['sia', 0.3], ['tia', 0.2], ['fia', 0.4], ['mia', 0.3]]
sf_lex = gsrln.lexeme('PV', sf2, 'suffix')

cands = generate_candidate(rt_lex, sf_lex)
for x in cands:
  print(DEP(x))
#=============================================================================