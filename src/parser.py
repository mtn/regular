from src.compiler import *
from src.util import *

class Parser:

    def __init__(self, regex):
        self.regex = regex
        self.ind = 0


    def advance(self):
        self.ind += 1

    def consume(self, letter):
        if not self.regex[self.ind] == letter:
            raise UnexpectedToken(letter, self.regex[self.ind])

        self.advance()

    def parseExpr(self):
        if self.regex[self.ind] == "|":
            self.parseOr()

    def parseOr(self):
        self.consume("|")
        self.consume("[")

        nestedStarts = []
        nestedOrs = {}
        startind = self.ind

        if "|[" in self.regex[self.ind:]:
            nextstart = self.regex[self.ind:].index("|[") + self.ind
        else:
            nextstart = -1

        endind = self.regex[self.ind:].index("]|") + self.ind

        while nextstart != -1 or nestedStarts:
            if nextstart != -1 and nextstart < endind:
                nestedStarts.append(nextstart)
                startind = nextstart + 2

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[") + startind
                else:
                    nextstart = -1
            else:
                beginNested = nestedStarts.pop()
                nestedOrs[beginNested] = endind
                startind = endind + 2

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[") + startind
                else:
                    nextstart = -1

                endind = self.regex[startind:].index("]|") + startind

        if nestedStarts:
            raise ParseError("Unmatched Or delimiters")

        print(nestedOrs)
        for k in nestedOrs:
            print(self.regex[k:nestedOrs[k]+2])
        alterns = splitInnerOr(self.regex[self.ind:endind], nestedOrs)
        print("ALTERNS")
        print(alterns)

        self.ind = endind
        self.consume("]")
        self.consume("|")

        return Or(list(map(lambda x: Parser(x).parseExpr(), alterns)))

def splitInnerOr(exp, nestedOrs):
    startind = 0
    split = []

    explen = len(exp)
    iterator = iter(range(explen))
    for i in iterator:
        if exp[i] == "|":
            split.append(exp[i:nestedOrs[i+2]])
            consume(iterator, nestedOrs[i+2] - i)
            startind = nestedOrs[i+2] + 1
        elif exp[i] == ",":
            split.append(exp[startind:i])
            startind = i + 1
        elif i == explen - 1:
            split.append(exp[startind:i+1])

    return split
