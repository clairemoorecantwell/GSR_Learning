#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#HL roots should take single-syllable suffixes, -a, -ga, -i, etc.
#LL and H roots should take two-syllable suffixes, -ia/-ina/-Cia, -aga, etc

#HH roots, and trisyllabic roots never violate Prosody
#function takes three strings : candidate, root, suffix 

import re



def syllable_structure (root_form):
	vowels = ['a', 'o', 'i', 'u', 'e']    
	syll_structure =[] #initialize list to store syll structure
	
	for i in range (0,len(root_form)):
	   
		if root_form[i] in vowels: #found a vowel
			if i==(len(root_form)-1): #last vowel -> L
				syll_structure.append("L")
			else:                     # not the last vowel
				if root_form [i+1] == ":": # if its a long vowel -> H
					syll_structure.append("H")
				else:                     # short vowel ->L
					syll_structure.append("L")

	syll_str_string = "".join(syll_structure) #join into a string 
	
	return syll_str_string


def prosody(candidate, suffix=None):
	#returns 1 if a candidate violates prosody, 0 otherwise
	
	if suffix is None:
		return 0
	
	monosyllabic_suffix = ["a","ga","i"]
	disyllabic_suffix = ["ia","ina","aga","aqi"]
		
	#to count for : togi but to:giina , root = candidate - suffix
	   
	suff_len = len(suffix)
	root_form = candidate [:-suff_len] #modified root form = candidate- suffix
			
	#print(root_form)
	syll_structure = syllable_structure(root_form)
   
	
	#if HL takes other than monosyll suffix > assign a violation   
	if syll_structure == "HL" and suffix not in monosyllabic_suffix:
		violation = 1
	
	#if LL takes other than disyllabic suffix > assing a violation
	elif syll_structure == "LL"  and suffix not in disyllabic_suffix :
		#if LL and -a
		violation = 1
			
	elif syll_structure =="H"  and suffix not in disyllabic_suffix:
		violation = 1
	else:
		violation = 0
	
	return violation 




#uniformity looks for (rs) in the candidate string 
#return 1 if there is a violation, 0 if there is no violation
def uniformity (candidate):
	
	violation = 0
	
	rs = re.search('(rs)',candidate.c)
	
	if rs:
		violation =1
		#if re returns a match violation =1
	return violation


def OCP(candidate):
	if re.search('(a{2}|e{2}|i{2}|o{2}|u{2})',candidate.c):
		return(1)
	else:
		return(0)
	
def DEP(cand):
	if cand.activityLevel > 1 or cand.activityLevel == 0: #if the candidate's activity level is greater than 1 or equals to 0, returns 0
		return 0
	else: # otherwise subtract the activity level from 1 and return
		return 1-cand.activityLevel
	
def NoCoda(candidate):
	if re.search('.*([^aeiou\)]|[^aeiou]\))$',candidate.c):
		return(1)
	else:
		return(0)

def MAX(cand):
	return cand.activityLevel #each candidate's activity level equals their reward points 


con = [prosody,uniformity,OCP,DEP,NoCoda,MAX]
conNames = ['prosody','uniformity','OCP','DEP','NoCoda','MAX']