#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 15:06:14 2022

@author: moorecantwell
"""

import learner as l
import constraints_Cshaped as c

g = l.Grammar("CshapedStartState.txt",l.Features("features.txt"),c.constraints,addViolations=True)







f = l.Features("features.txt")

x = f.stringToF("ts")


lex = g.trainingData.lexicon["word100"]



# why only three constraint weights?