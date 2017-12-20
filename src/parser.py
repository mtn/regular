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

    def _handleor_start(self, nested_or_starts, or_start, startind):
        nested_or_starts.append(or_start)
        startind = or_start + 2

        if "|[" in self.regex[startind:]:
            or_start = self.regex[startind:].index("|[") + startind
        else:
            or_start = -1

        return or_start, startind

    def _handleor_end(self, begin_nested, nested_ors, startind, or_end):
        nested_ors[begin_nested] = or_end
        startind = or_end + 2

        if "|[" in self.regex[startind:]:
            or_start = self.regex[startind:].index("|[") + startind
        else:
            or_start = -1

        or_end = self.regex[startind:].index("]|") + startind

        return or_start, or_end


    def _handlezero_start(self, nested_zero_starts, or_start, startind):
        nested_zero_starts.append(or_start)
        startind = or_start + 2

        if "*(" in self.regex[startind:]:
            zero_start = self.regex[startind:].index("*(") + startind
        else:
            zero_start = -1

        return zero_start, startind

    def _handleZeroEnd(self, begin_nested, zeros, startind, zeroend):
        print("INSIDE HANDLE ZERO END")
        print("zeros {}".format(zeros))
        zeros[begin_nested] = zeroend
        startind = zeroend + 1

        print("zeros {}".format(zeros))

        if "*(" in self.regex[startind:]:
            zero_start = self.regex[startind:].index("*(") + startind
        else:
            zero_start = -1

        or_end = self.regex[startind:].index(")") + startind

        return zero_start, zeroend

    def parseOr(self):
        """
        Parse an alternation starting at current index
        """

        self.consume("|")
        self.consume("[")

        nested_or_starts = []
        nested_zero_starts = []
        nested_ors = {}
        inner_zeros = {}
        startind = self.ind

        if "|[" in self.regex[self.ind:]:
            or_start = self.regex[self.ind:].index("|[") + self.ind
        else:
            or_start = -1

        if "*(" in self.regex[self.ind:]:
            zero_start = self.regex[self.ind:].index("*(") + self.ind
            zeroend = self.regex[self.ind:].index(")") + self.ind
        else:
            zero_start = -1

        or_end = self.regex[self.ind:].index("]|") + self.ind

        while or_start != -1 or zero_start != -1 or nested_or_starts:

            if or_start != -1 and or_start < or_end or \
                zero_start != -1 and zero_start < zeroend:

                if or_start != -1 and zero_start != -1:
                    if or_start < zero_start:
                        or_start, startind = self._handleor_start(nested_or_starts,
                                                                  or_start, startind)
                    else:
                        print("zero_start")
                        zero_start, startind = self._handlezero_start(nested_zero_starts,
                                                                      zero_start, startind)
                        print("nested_zero_starts {}".format(nested_zero_starts))
                elif or_start != -1:
                    or_start, startind = self._handleor_start(nested_or_starts,
                                                              or_start, startind)
                elif zero_start != -1:
                    print("zero_start")
                    zero_start, startind = self._handlezero_start(nested_zero_starts,
                                                                  zero_start, startind)
                    print("nested_zero_starts {}".format(nested_zero_starts))

            else:
                if nested_zero_starts:
                    zero_next = nested_zero_starts[-1]
                else:
                    zero_next = nested_or_starts[-1] + 1

                if nested_or_starts:
                    or_next = nested_or_starts[-1]
                else:
                    or_next = nested_zero_starts[-1] + 1

                print("nested_zero {} or_next {}".format(zero_next, or_next))

                if nested_zero_starts:
                    print("hi zeroend")
                    begin_nested = nested_zero_starts.pop()
                    zero_start, zeroend = self._handleZeroEnd(begin_nested,
                                                              inner_zeros, startind,
                                                              or_end)
                else:
                    begin_nested = nested_or_starts.pop()
                    or_start, or_end = self._handleor_end(begin_nested,
                                                          nested_ors,
                                                          startind, or_end)

        if nested_or_starts:
            raise ParseError("Unmatched Or delimiters")

        print("zeros {}".format(inner_zeros))
        print("ors {}".format(nested_ors))
        alterns = split_inner_or(self.regex[self.ind:or_end], nested_ors, inner_zeros)
        print(alterns)

        self.ind = or_end
        self.consume("]")
        self.consume("|")

        return Or(list(map(lambda x: Parser(x).parseExpr(), alterns)))

def split_inner_or(exp, ors, zeros):
    """
    Break up inside of Or expression into a list for further parsing
    Commas/string end are the delimiters, except within nested expressions
    """

    startind = 0
    split = []

    explen = len(exp)
    iterator = iter(range(explen))
    for i in iterator:
        if exp[i] == "|":
            split.append(exp[i:ors[i+2]])
            consume(iterator, ors[i+2] - i)
            startind = ors[i+2] + 1
        elif exp[i] == "*":
            split.append(exp[i:zeros[i+2]])
            consume(iterator, zeros[i+2] - i)
            startind = zeros[i+2] + 1
        elif exp[i] == ",":
            split.append(exp[startind:i])
            startind = i + 1
        elif i == explen - 1:
            split.append(exp[startind:i+1])

    return split
