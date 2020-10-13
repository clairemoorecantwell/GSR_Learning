import re
candidate = ""

def OCP(candidate):
    if re.search('(a{2}|e{2}|i{2}|o{2}|u{2})',candidate):
        return(False)
    else:
        return(True)