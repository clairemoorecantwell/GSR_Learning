#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 14:01:48 2020

@author: juliazaborna
"""

from pandas import read_excel

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

def prosody_violations_ina_a (candidate, root, suffix):
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



    
def read_input(file_name, sheet_number):
        
    #reading excel into dataframe
    input_dt_frame = read_excel(file_name, sheet_number ) #this is for the sheet#1; 
        #dataframe into np array
    input_np = input_dt_frame.to_numpy()

    return input_np

learning_input = read_input("learning_input.xlsx", 0)
#print(learning_input)
'''
num =1
count_violations = 0
for row in learning_input:
    candidate = row[0]
    suffix = row[3]
    root = row[5]
    num +=1
    violates = prosody(candidate, root, suffix)
    count_violations +=violates
    if violates:
        print(str(num) + " " + candidate +" " + root+" "+ suffix)
    
    
print("total violations " + str(count_violations))
print(num)  
#21% violate 
'''
print("for -a, -ina only")
num =1
count_violations = 0
for row in learning_input:
    candidate = row[0]
    suffix = row[3]
    root = row[5]
    num +=1
    violates = prosody_violations_ina_a(candidate, root, suffix)
    count_violations +=violates
    if violates:
        print(str(num) + " " + candidate +" " + root+" "+ suffix)
        
print("total violations " + str(count_violations))
print(num) 