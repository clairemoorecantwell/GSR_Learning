# import things that need to be imported here

#####################################################


class lexeme:
    def __init__(self, tag, allomorphs, kind):
        self.tag = tag # label for the lexeme, so the humans can easily see what it is.  ex. 'tagi' '-ina', even things like 'PV' or '3rdsing'
        self.allomorphs = allomorphs # list of allomorphs, in the following format:

# [[ 'string', 1],    <-- number is activity level of thematic C.  We will assume that thematic C's are firs in suffixes, last in roots
#  [ 'tagis',  0.7],        
#  [ 'tagi',   0.0],
#  ...
# ]]

# [[ 'ia',  0.0],
#  [ 'ina', 0.0],
#  [ 'a',  0.0],
#  [ 'sia', 0.4],
# ...
# ]]

        self.kind = kind # string specifying what kind of morpheme it is.  'root' 'suffix' 'prefix' etc.
        self.freq = 0   #initialize at zero, increase during learning
        


class Lexicon:
    def __init__(self):
        self.lexemeList = []  #initialise empty list for storing lexemes in
        self.freqList = []    #empty list for storing each lexeme's frequency - used for sampling
        
        
    def add_lexeme(self,l):
        # Add a lexeme to the lexemeList
        self.lexemeList(l)
        self.freqList.append(l.freq)
        
    
    def update_freqList(self):
        # update freqList with all lexemes' frequencies, in case they have changed
        self.freqList = []
        for l in self.lexemeList:
            self.freqList.append(l.freq)


    def sample(self, n):  # sample 

        
