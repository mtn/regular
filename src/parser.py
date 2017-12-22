from src.compiler import *
from src.util import *

class Parser:

    def __init__(self, regex):
        self.regex = regex
        self.ind = 0

    def advance(self):
        self.ind += 1
        return self.regex[self.ind - 1]

    def consume(self, token):
        if not self.regex[self.ind] == token:
            raise UnexpectedToken(token, self.regex[self.ind])

        self.advance()

    def parse(self):
        exps = []
        while self.ind < len(self.regex):
            exps.append(self.parse_expr())

        if len(exps) == 1:
            return exps[0]

        return exps

    def parse_expr(self):
        if self.regex[self.ind] == "|":
            return self.parse_or()
        elif self.regex[self.ind] == "*":
            return self.parse_zero_or_more()
        elif self.regex[self.ind] == "_":
            self.advance()
            return Any()

        return self.advance()

    def _handle_or_start(self, nested_or_starts, or_start, startind):
        nested_or_starts.append(or_start)
        startind = or_start + 2

        if "|[" in self.regex[startind:]:
            or_start = self.regex[startind:].index("|[") + startind
        else:
            or_start = -1

        return or_start, startind

    def _handle_or_end(self, begin_nested, nested_ors, startind, or_end):
        nested_ors[begin_nested] = or_end
        startind = or_end + 2

        if "|[" in self.regex[startind:]:
            or_start = self.regex[startind:].index("|[") + startind
        else:
            or_start = -1

        or_end = self.regex[startind:].index("]|") + startind

        return or_start, or_end


    def _handle_zero_start(self, nested_zero_starts, or_start, startind):
        nested_zero_starts.append(or_start)
        startind = or_start + 2

        if "*(" in self.regex[startind:]:
            zero_start = self.regex[startind:].index("*(") + startind
        else:
            zero_start = -1

        return zero_start, startind

    def _handle_zero_end(self, begin_nested, zeros, startind, zeroend):
        zeros[begin_nested] = zeroend
        startind = zeroend + 1

        if "*(" in self.regex[startind:]:
            zero_start = self.regex[startind:].index("*(") + startind
        else:
            zero_start = -1

        or_end = self.regex[startind:].index(")") + startind

        return zero_start, zeroend

    def parse_or(self):
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
                        or_start, startind = self._handle_or_start(nested_or_starts,
                                                                   or_start, startind)
                    else:
                        print("zero_start")
                        zero_start, startind = self._handle_zero_start(nested_zero_starts,
                                                                       zero_start, startind)
                        print("nested_zero_starts {}".format(nested_zero_starts))
                elif or_start != -1:
                    or_start, startind = self._handle_or_start(nested_or_starts,
                                                               or_start, startind)
                elif zero_start != -1:
                    print("zero_start")
                    zero_start, startind = self._handle_zero_start(nested_zero_starts,
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
                    zero_start, zeroend = self._handle_zero_end(begin_nested,
                                                                inner_zeros, startind,
                                                                or_end)
                else:
                    begin_nested = nested_or_starts.pop()
                    or_start, or_end = self._handle_or_end(begin_nested,
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

        return Or(list(map(lambda x: Parser(x).parse(), alterns)))

    def parse_zero_or_more(self):
        pass

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
            iter_consume(iterator, ors[i+2] - i)
            startind = ors[i+2] + 1
        elif exp[i] == "*":
            split.append(exp[i:zeros[i+2]])
            iter_consume(iterator, zeros[i+2] - i)
            startind = zeros[i+2] + 1
        elif exp[i] == ",":
            split.append(exp[startind:i])
            startind = i + 1
        elif i == explen - 1:
            split.append(exp[startind:i+1])

    return split
