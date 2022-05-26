import learner as l

t = l.trainingData("useListed_input")

#Check how the training data got entered
t.lexicon
t.learnData
t.tableaux
# look at the input tableaux in detail
t.constraintNames
for tab in t.tableaux:
    print(tab)
    
t.tabProb


# Need to find out if a useListed tableau can actually be created
# First create a grammar object with the same input file
# we'll use None for the feature set, and see how that goes

g = l.Grammar("useListed_input",l.Features("features.txt"))
t = g.trainingData
g.w

newTab = g.makeTableau(t.learnData[1])

g.p_useListed

g.learn(1000,100)
