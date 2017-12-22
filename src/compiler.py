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

            if state.matchEnd() and i == len(chars) - 1:
                return True
            elif state.matchEnd() and not state.canMatchMore():
                return False

        return False

def compile_string(string, tail=EmptyString()):
    for char in reversed(string):
        tail = CharacterNode(char, tail)

    return tail

def compile_list(arr, tail=EmptyString()):
    for regex in reversed(arr):
        tail = _compile(regex, tail)

    return tail

def compile_or(altern, tail=EmptyString()):
    return AlternationFactory(list(map(lambda a: _compile(a, tail), altern.alternatives)))

def compile_any(tail=EmptyString()):
    return AnyCharacterNode(tail)

def compile_zero_or_more(zeroOrMore, tail=EmptyString()):
    repetition = RepetitionNode(tail)

    contents = _compile(zeroOrMore.repeatable, repetition)
    repetition.head = contents

    return repetition

def _compile(regex, tail=EmptyString()):
    if isinstance(regex, str):
        return compile_string(regex, tail)
    elif isinstance(regex, list):
        return compile_list(regex, tail)
    elif isinstance(regex, Or):
        return compile_or(regex, tail)
    elif isinstance(regex, ZeroOrMore):
        return compile_zero_or_more(regex, tail)
    elif isinstance(regex, Any):
        return compile_any(tail)
    else:
        raise TypeError("Unexpected internal type: {}".format(type(regex)))
