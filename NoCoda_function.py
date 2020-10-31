import re
candidate = ""

def NoCoda(candidate):
    if re.search('.*([^aeiou\)]|[^aeiou]\))$',candidate):
        return(1)
    else:
        return(0)
