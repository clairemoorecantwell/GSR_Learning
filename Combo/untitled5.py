#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def Max(faithCand,richCand=None,generate = False):
	'''Rewarding constraint.  Returns a positive number: the sum of all activity levels from faithCand that are realized in richCand'''
	if generate:
		return richCand
	else:
		#evaluate richCand wrt faithCand and return a violation
		viol = 0
		for s in richCand.segsList:
			if s in faithCand.segsList:
				viol += faithCand.activitys[]
	