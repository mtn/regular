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
            return self.parseOr()

        return self

    def _handleOrStart(self, nestedOrStarts, orstart, startind):
        nestedOrStarts.append(orstart)
        startind = orstart + 2

        if "|[" in self.regex[startind:]:
            orstart = self.regex[startind:].index("|[") + startind
        else:
            orstart = -1

        return orstart, startind

    def _handleOrEnd(self, beginNested, nestedOrs, startind, endind):
        nestedOrs[beginNested] = endind
        startind = endind + 2

        if "|[" in self.regex[startind:]:
            orstart = self.regex[startind:].index("|[") + startind
        else:
            orstart = -1

        endind = self.regex[startind:].index("]|") + startind

        return orstart, endind


    def _handleZeroStart(self, nestedZeroStarts, orstart, startind):
        nestedZeroStarts.append(orstart)
        startind = orstart + 2

        if "*(" in self.regex[startind:]:
            zerostart = self.regex[startind:].index("*(") + startind
        else:
            zerostart = -1

        return zerostart, startind

    def _handleZeroEnd(self, beginNested, zeros, startind, endind):
        zeros[beginNested] = endind
        startind = endind + 1

        if "*(" in self.regex[startind:]:
            zerostart = self.regex[startind:].index("*(") + startind
        else:
            zerostart = -1

        endind = self.regex[startind:].index(")") + startind

        return zerostart, endind

    def parseOr(self):
        """
        Parse alternations
        """

        self.consume("|")
        self.consume("[")

        nestedOrStarts = []
        nestedZeroStarts = []
        nestedOrs = {}
        innerZeroOrMores = {}
        startind = self.ind

        if "|[" in self.regex[self.ind:]:
            orstart = self.regex[self.ind:].index("|[") + self.ind
        else:
            orstart = -1

        if "*(" in self.regex[self.ind:]:
            zerostart = self.regex[self.ind:].index["*("] + self.ind
        else:
            zerostart = -1

        endind = self.regex[self.ind:].index("]|") + self.ind

        while orstart != -1 or zerostart != -1 or nestedOrStarts:

            if orstart != -1 and orstart < endind or \
                zerostart != -1 and zerostart < endind:

                if orstart != -1 and zerostart != -1:
                    if orstart < zerostart:
                        orstart, startind = self._handleOrStart(nestedOrStarts,
                                orstart, startind)
                    else:
                        zerostart, startind = self._handleZeroStart(nestedZeroStarts,
                                zerostart, startind)
                elif orstart != -1:
                    orstart, startind = self._handleOrStart(nestedOrStarts,
                            orstart, startind)
                elif zerostart != -1:
                    zerostart, startind = self._handleOrStart(nestedZeroStarts,
                            zerostart, startind)

            else:
                if nestedOrStarts[-1] < nestedZeroStarts[-1]:
                    beginNested = nestedOrStarts.pop()
                    orstart, endind  = self._handleOrEnd(beginNested, nestedOrs,
                            startind, endind)
                else:
                    beginNested = nestedZeroStarts.pop()
                    zerostart, endind  = self._handleZeroEnd(beginNested,
                            innerZeroOrMores, startind, endind)

        if nestedOrStarts:
            raise ParseError("Unmatched Or delimiters")

        alterns = splitInnerOr(self.regex[self.ind:endind], nestedOrs)
        print(alterns)

        self.ind = endind
        self.consume("]")
        self.consume("|")

        return Or(list(map(lambda x: Parser(x).parseExpr(), alterns)))

def splitInnerOr(exp, nestedOrs):
    """
    Break up inside of Or expression into a list for further parsing
    """

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

