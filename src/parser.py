from src.compiler import *



def parseRegex(inp):
    try:
        regex, word = inp.split(":")
    except:
        print("Incorrect input format")
        exit(1)

    regex = _parse(regex)

    return RE(regex).match(word)

def _parse(regex):

    if regex[0] == "_":
        return Any()
    elif regex[0] == "[":
        return parseList()

    print(regex)

def parseList():
    pass
