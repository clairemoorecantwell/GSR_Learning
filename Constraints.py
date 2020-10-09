#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 12:32:22 2020

@author: juliazaborna
"""

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


def prosody_violations (candidate, root, suffix):
    #returns 1 if a candidate violates prosody, 0 otherwise
    
    if suffix == 'ina' or suffix == 'a' or suffix == "ia":
        
        #to count for : togi but to:giina , root = candidate - suffix
       
        suff_len = len(suffix)
        root_form = candidate [:-suff_len] #root form = candidate- suffix
            
        #print(root_form)
        syll_structure = syllable_structure(root_form)
        #print (syll_structure)
        #print (suffix)
        
        if syll_structure == "HL" and suffix!="a": #if HL and -ia/ina
            violation = 1

        elif syll_structure == "LL" and suffix =="a": #if LL and -a
            violation = 1
            
        elif syll_structure =="H"  and suffix =="a": #if H and -a
            violation = 1
        else:
            violation = 0
           
        
            

        
        
    else:
        violation = 0
        
    
        
    return violation 



#print(prosody_violations("ta:giina", "tagi", "ina")) #no violation 
    
#test syllab_structure
'''
print(syllable_structure("ta:gis"))
print(syllable_structure("ta:gi"))
print(syllable_structure("tagi"))
print(syllable_structure("tagi:"))
'''
#print(prosody_violations("tagia", "tagi", "a") )    # violation  returns 1
#print(prosody_violations("tagiia", "tagi", "ia"))   #no violation  0
#print(prosody_violations("o:sia", "osi", "a"))      #no violation > 0
#print(prosody_violations("o:siina", "to", "ina"))  # violation 1 


def uniformity (candidate, suffix, root):
    
    
    
    
    violation =0
    
    
    return violation
