import re
candidate = ""

def NoCoda(candidate):
    if re.search('.*([^aeiou\)]|[^aeiou]\))$',candidate):
        return(False)
    else:
        return(True)
