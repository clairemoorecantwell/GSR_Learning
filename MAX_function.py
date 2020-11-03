# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 21:25:51 2020

@author: richa
"""

##############
# evaluate candidates by MAX constraint and assign rewards
##############

#Function: evaluate candidates by MAX constraint and assign rewards

#Input: one candidate object (defined in the candidate class)
#Output: reward points

from GenerateCandidate_function import generate_candidate
import GSRlearner as gsrln

def MAX(cand):
    return cand.activityLevel #each candidate's activity level equals their reward points 


#Test data
#=============================================================================
rt2 = [['tagis', 0.4]]
rt_lex = gsrln.lexeme('tagi', rt2, 'root')

sf2 = [['ina', 0.3], ['a', 0.3], ['sia', 0.3], ['tia', 0.2], ['fia', 0.4], ['mia', 0.3]]
sf_lex = gsrln.lexeme('PV', sf2, 'suffix')

cands = generate_candidate(rt_lex, sf_lex)
for x in cands:
  print(MAX(x))
#=============================================================================
