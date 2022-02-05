# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 11:10:01 2021

@author: moore-cantwell
"""
import learner as l

# Testing the file input
# Basic lexeme file:

t = l.trainingData("basic_lexeme_inpt")

# see the lexemes:
t.lexTags
t.learnData
print(t)

t = l.trainingData("frequency_lexeme_input")

# see the lexemes:
t.lexTags
t.learnData
print(t)


t = l.trainingData("input_small.txt")

# see the lexemes:
t.lexTags
t.learnData
print(t)

import constraints as c
g = l.Grammar("frequency_lexeme_input",c.constraints, c.operations, l.Features("features.txt"))

t = l.trainingData("input.txt")
