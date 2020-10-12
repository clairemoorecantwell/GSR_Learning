#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 12:32:22 2020

@author: juliazaborna
"""
#HL roots should take single-syllable suffixes, -a, -ga, -i, etc.
#LL and H roots should take two-syllable suffixes, -ia/-ina/-Cia, -aga, etc

#HH roots, and trisyllabic roots never violate Prosody
#function takes three strings : candidate, root, suffix 

vowels = ['a', 'o', 'i', 'u', 'e']


def syllable_structure (root_form):
    
    
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


def prosody(candidate, root, suffix):
    #returns 1 if a candidate violates prosody, 0 otherwise
    
    monosyllabic_suffix = ["a","ga","i"]
    disyllabic_suffix = ["ia","ina","aga"]
        
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



#print(prosody_violations("ta:giina", "tagi", "ina")) #no violation 
    
#test syllab_structure

#print(syllable_structure("ta:gis"))
'''
print(syllable_structure("ta:gi"))
print(syllable_structure("tagi"))
print(syllable_structure("tagi:"))
'''
#print(prosody("tagia", "tagi", "a") )    # violation  returns 1

#print(prosody("tolopo:ina", "tolopo", "ina"))
#print(prosody_violations("tagiia", "tagi", "ia"))   #no violation  0
#print(prosody_violations("o:sia", "osi", "a"))      #no violation > 0
#print(prosody_violations("o:siina", "to", "ina"))  # violation 1 



def uniformity (candidate, suffix, root):
    
    
    
    
    violation =0
    
    
    return violation
