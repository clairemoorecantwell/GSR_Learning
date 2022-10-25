    def makeTableau(self, datum):
        '''Make the tableau for learning, given all the parameters'''
        ''' datum is an entry in a trainingData.learnData object'''
        ''' it has the form [[lexeme1,lexeme2,...],surface string, input string]'''
        method = "deNovo"
        # "deNovo": create a brand new tableau, with generated candidates.  For this we need operations, and constraints defined as functions
        # "partial": use user-defined candidates, but add violations of a few markedness constraints
        # "full": completely user-defined, except for perhaps the PFCs

        # Determine the creation method, and make sure we have everything for it
        # Right now only "full" is implemented
        if not self.generateCandidates:
            if not self.addViolations:
                method = "full"
            elif self.constraints:  # constraint functions must exist for them to be used to assign new violations
                method = "partial"
            else:
                print("ERROR: you must define a set of constraint functions")
                exit
        else:
            if self.constraints and self.operations:
                # TODO fill this out for UseListed; it might not work as expected at the moment.
                return createTableau(lexemes, self.constraints, self.operations, self.featureSet, datum[1], w=self.w[:])
            else:
                print("ERROR: you cannot generate candidates without predefined operations and constraints")

        # Initial tableau creation, from the input file
        tab = self.trainingData.tableaux[self.trainingData.tableauxTags.index(datum[2])].copy()
        tab.w = self.w[:]
        tab.constraintList = self.trainingData.constraintNames[:]
        # print(tab)

        ############################### UseListed tableau creation
        # listed = False # Are we using a specially listed lexical item?  If False, we compose from extant lexical items

        # Check if we should use a listed form - is there a listed form in the lexicon?
        listedTag = "_".join([i.tag for i in datum[0]]) if len(datum[0]) > 1 else False
        r = random.random()  # sample to determine whether we do listing or composition on this particular trial
        if listedTag in self.trainingData.lexicon and 1 < self.p_useListed < 2:  # we're sampling based on frequency
            f_composed = [lex.freq for lex in datum[0]]
            f_listed = self.trainingData.lexicon[listedTag].freq
            #########################################################
            ## To change how listed forms are sampled based on frequency edit here
            #########################################################
            # choose the lowest frequency lexeme of the bunch
            local_p_useListed = f_listed / (f_listed + min(f_composed))

            # choose the root's frequency, if there is exactly one root
            # roots = [1 if lex.kind =='root' else 0 for lex in datum[0] ]

            # if sum(roots) == 1:
            #   f_root = f_composed[roots.index(1)]
            #   local_p_useListed = f_listed/(f_listed + f_root)
            # else:
            #   local_p_useListed = f_listed/(f_listed + min(f_composed))
            #########################################################
            print("f_composed:" + str(f_composed))
            print("f_listed:" + str(f_listed))
            print("p_uselisted")
            print(local_p_useListed)
        else:
            local_p_useListed = self.p_useListed
        if listedTag and listedTag in self.trainingData.lexicon and r < local_p_useListed:
            # we're just updating BOTH the parts and the whole listed form's frequency
            # (Parts updated above, in the main learning loop)
            self.trainingData.lexicon[listedTag].lastSeen = self.t
            self.trainingData.lexicon[listedTag].freq += 1

            # Check if we are using hidden structure to do this, or choosing between listing and composing
            if self.p_useListed >= 2:  # for now, set p_uselisted to 2 or higher to indicate "use hidden structure"
                # Build hidden structure tableau
                # note candidates as coming from one lexeme or another
                # and copy candidates over
                for lex in datum[0]:
                    lex.lastSeen = self.t
                    lex.freq += 1
                origCandidates = tab.candidates[:]
                for cand in origCandidates:
                    newC = cand.copy()
                    cstring = cand.c
                    newC.c = "listed_" + cstring
                    cand.c = "composed_" + cstring

                    # self.cPairs is a tuple (list_of_pairs, reverse_sorted_indices_of_listed, UseListed violation index before _listed removal)
                    newC.violations[self.cPairs[2]] = 0
                    cand.violations[self.cPairs[2]] = 1

                    for pair in self.cPairs[0]:  # assign violations of faith to _listed versus not
                        # the tuple is (composedIndex,listedIndex)
                        newC.violations[pair[0]] = newC.violations[pair[1]]  # set both columns to the _listed version
                        cand.violations[pair[1]] = cand.violations[
                            pair[0]]  # set both columns to the regular (composed) version

                    for i in self.cPairs[
                        1]:  # Now remove the violation corresponding to the _listed form of the constraint
                        newC.violations.pop(i)
                        cand.violations.pop(i)

                    tab.addCandidate(newC)

            elif r < local_p_useListed:  # Only using the listed form in the tableau
                print("Using the listed form only!")
                useListedIndex = self.cPairs[2]
                for cand in tab.candidates:
                    if useListedIndex is not None:  # If the useListed constraint exists (for hidden structure only)
                        cand.violations[self.cPairs[2]] = 0  # setting the value for UseListed
                    for pair in self.cPairs[0]:
                        cand.violations[pair[0]] = cand.violations[pair[1]]  # Only use the _listed version
                    for i in self.cPairs[1]:
                        cand.violations.pop(i)

            # lexemes = self.trainingData.lexicon[listedTag]

        else:
            '''no listed form - can get here 3 ways:
            (1) if listing is turned off (p_useListed ==0)
            (2) if listing was not selected on this trial
            (3) if the listed version isn't in the lexicon yet
            # exclude listeds if there are any - simply delete the column from the tableau
            # remove their violations from every candidate
            '''
            for lex in datum[0]:  # This little bit is redundant with above, and also in the main update() loop
                lex.lastSeen = self.t
                lex.freq += 1
            if self.p_useListed:
                for cand in tab.candidates:
                    for i in self.cPairs[1]: # note that cPairs might be empty, even if are doing UseListed, if all faithfulness constraints are assigned by function
                        cand.violations.pop(i)

        #################################################################################

        ######################################################################
        # Adjust for lexically indexed C's
        if self.lexC_type:
            for cIndex in range(0, len(tab.w)):  # run through all constraints
                wToUse = 0
                for lex in datum[0]:  # run through all lexemes
                    lexIndexForC = lex.lexCindexes[cIndex]  # which idex does lex use?
                    thisW = self.lexCs[cIndex][lexIndexForC]  # what's the weight associated with that index?
                    if thisW > wToUse:  # if it's larger than we've seen before
                        wToUse = thisW  # keep it
                if wToUse:  # if there was any weight above 0
                    tab.w[cIndex] = wToUse  # use that clone weight instead of the base weight

        ######################################################################

        if method == "partial":
            # Assign violations of dynamic constraints
            #tab.constraintList += [c.name for c in self.constraints]
            UR = ""
            for lexeme in datum[0]:
                UR += lexeme.toUR()
            for cand in tab.candidates:
                for con in self.constraints:
                    cand.violations.append(con.assignViolations(UR,cand))# self.featureSet))

        tab.applyPFCs()

        return tab  # , tabconstraintList, w



def createTableau(lexemes, constraints, operations, featureSet, obsOutput, w=None, scramble=False):
    '''create a tableau from lexemes, constraints, operations'''
    # lexemes is an ordered list of lexemes, or a single lexeme
    # TODO expand to more than two lexemes
    # TODO separate out markedness and faithfulness
    # constraints, operations, are lists of functions.  see constraints.py for details
    if not w:
        w = [0 for c in constraints]
    constraintList = [c.name for c in constraints]

    if not scramble:
        individualCands = []
        for l in lexemes:
            individualCands.append(l.toRichCand(featureSet))
        if len(lexemes) > 1:
            faiths = list(itertools.product(individualCands[0], individualCands[1]))
        else:
            faiths = individualCands
    # TODO This is where it's limited to two lexemes only

    # TODO implement scramble option

    # concatenate richCands
    fcs = []  # 'fc' = 'faithful candidate'
    containsObsOut = 0
    for fc in faiths:
        # begin creating the new richCand
        newSegsList = fc[0].segsList[:]
        newSegsDict = fc[0].segsDict.copy()
        newActivitys = fc[0].activitys[:]
        newSuprasegmentals = fc[0].suprasegmentals[:] if fc[0].suprasegmentals else []
        for i in range(1, len(fc)):  # go through morphemes
            # concatenate seglist
            newSegsList += [seg + '_w' + str(i + 1) for seg in fc[i].segsList[:]]
            for seg in fc[i].segsList:
                # concatenate segsDict
                newSegsDict[seg + '_w' + str(i + 1)] = fc[i].segsDict[seg][:]
            newActivitys += fc[i].activitys[:]
            newSuprasegmentals += fc[i].suprasegmentals[:] if fc[
                i].suprasegmentals else []  # Note that suprasegmentals is now an empty list if there are none, instead of NoneType
        # TODO change richCand() so that empty list is the default if there are no suprasegmentals
        newC = featureSet.featureToS(newSegsDict, newSegsList)
        obsProb = 1 if newC == obsOutput else 0
        containsObsOut = 1 if newC == obsOutput else 0

        fcs.append(richCand(newC, [], obsProb, newSegsDict, newSegsList, None, newActivitys, newSuprasegmentals,
                            surfaceForm=newC))

    # Assign markedness violations to faithful candidates
    cs = [c.c for c in fcs]
    for fc in fcs:
        for con in constraints:
            fc.violations.append(con.assignViolations(fc, featureSet))

    allCands = fcs
    # for c in allCands:
    #   print(c)

    # Generate new candidates, dropping off at a rate controlled by A as you get farther down the 'tree' and rejecting them if they are not harmonically improving, according to s
    moarCandidates = 1
    t = 1  # 'time', or the depth in the tree
    A = 10  # higher -> more candidates (keep traversing the tree)
    s = 20  # sigmoid parameter  higher--> more candidates
    while moarCandidates:
        for o in operations:
            for c in allCands:
                # apply o with probability A/t
                if random.random() < A / t or not (containsObsOut):  # Continue to generate candidates until you generate the observed output
                    try:
                        candidates = o(c, featureSet)
                    except:
                        print("Error, trying to apply operation  to candidate ", c)
                    if type(candidates) == tuple:
                        candidates, *_ = candidates
                    # print(candidates)
                    candidates = [can for can in candidates if can.c not in cs]
                    # TODO check operations list also to establish sameness
                    for possibleCand in candidates:
                        for con in constraints:
                            # print('1')
                            #   print(con.name)
                            possibleCand.violations.append(con.assignViolations(possibleCand, featureSet))
                        #   print("violations: ",possibleCand.c)
                        #   print(possibleCand.violations)

                        # for possibleCand in candidates:
                        #   print(possibleCand.violations)

                        if possibleCand.surfaceForm == obsOutput:
                            containsObsOut = 1
                            possibleCand.observedProb = 1
                            allCands.append(possibleCand)
                            cs.append(possibleCand.c)
                        else:
                            possibleCand.harmony = -sum(
                                viol * weight for viol, weight in zip(possibleCand.violations, w))
                            Hdiff = possibleCand.harmony - c.harmony
                            p_keep = (1 / 2) * Hdiff / math.sqrt(
                                s + Hdiff ** 2) + 0.5  # Here is the equation for keeping a candidate based on harmony
                            if random.random() < p_keep:
                                possibleCand.observedProb = 1 if possibleCand.surfaceForm == obsOutput else 0
                                allCands.append(possibleCand)
                                cs.append(possibleCand.c)

        t += 1
        if random.random() < (1 - (A / t)) ** (len(operations)) or not (containsObsOut):
            # Halt candidate generation
            moarCandidates = 0

    # assign PFC violations:

    wNum = 0
    for l in lexemes:
        if l.PFCs:
            for pfc in l.PFCs:
                if wNum:
                    for cand in allCands:
                        # Have to actually make a copy to evaluate
                        # fill in 'w2', 'w3' etc on segment labels on the candidates
                        newPFC = PFC(pfc.w, pfc.feature, pfc.seg, pfc.seg2, pfc.typ)
                        newPFC.seg = newPFC.seg + '_w' + str(wNum + 1) if newPFC.seg else None
                        newPFC.seg2 = newPFC.seg2 + '_w' + str(wNum + 1) if newPFC.seg2 else None
                        cand.violations.append(newPFC.evaluate(cand))
                        cand.harmony += -cand.violations[-1] * newPFC.w
                else:
                    for cand in allCands:
                        cand.violations.append(pfc.evaluate(cand))
                        cand.harmony += -cand.violations[-1] * pfc.w
                constraintList.append((pfc.name, pfc))
                w.append(pfc.w)
        wNum += 1

    tab = Tableau("_".join([l.tag for l in lexemes]))
    for cand in allCands:
        tab.addCandidate(cand)

    return tab, constraintList, w

