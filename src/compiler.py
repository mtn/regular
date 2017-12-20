"""
Generates traversable linked list from internal representation

"abc": match characters in string
[a,b,c...]: concatenation
Or([a,b,c]): alternation
ZeroOrMore(re): repetition
Any: wildcard
"""

from src.nodes import *


class Or:
    def __init__(self, alternatives):
        if not isinstance(alternatives, list):
            raise TypeError("Argument to Or must be a list")

        self.alternatives = alternatives

    def __repr__(self):
        return "Or({})".format(self.alternatives)

class ZeroOrMore:
    def __init__(self, repeatable):
        self.repeatable = repeatable

    def __repr__(self):
        return "ZeroOrMore({})".format(self.repeatable)

class Any:
    def __repr__(self):
        return "Any"

class RE:
    def __init__(self, regex):
        self.start = _compile(regex)

    def match(self, inp):
        state = self.start
        chars = list(inp)

        if not chars and state.matchEnd():
            return True

        for i, c in enumerate(chars):
            state = state.derive(c)

            if state.matchEnd():
                return True
            elif state.matchEnd() and not state.canMatchMore():
                return False

        return False

def compileString(string, tail=EmptyString()):
    for char in reversed(string):
        tail = CharacterNode(char, tail)

    return tail

def compileList(arr, tail=EmptyString()):
    for regex in reversed(arr):
        tail = _compile(regex, tail)

    return tail

def compileOr(altern, tail=EmptyString()):
    return AlternationNode(list(map(lambda a: _compile(a, tail), altern.alternatives)))

def compileAny(tail=EmptyString()):
    return AnyCharacterNode(tail)

def compileZeroOrMore(zeroOrMore, tail=EmptyString()):
    repetition = RepetitionNode(tail)

    contents = _compile(zeroOrMore.repeatable, repetition)
    repetition.head = contents

    return repetition

def _compile(regex, tail=EmptyString()):
    if isinstance(regex, str):
        return compileString(regex, tail)
    elif isinstance(regex, list):
        return compileList(regex, tail)
    elif isinstance(regex, Or):
        return compileOr(regex, tail)
    elif isinstance(regex, ZeroOrMore):
        return compileZeroOrMore(regex, tail)
    elif isinstance(regex, Any):
        return compileAny(tail)
    else:
        raise TypeError("Unexpected internal type")

