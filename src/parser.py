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

    def _handle_or_start(self, nested_or_starts, or_start, start_ind):
        nested_or_starts.append(or_start)
        start_ind = or_start + 2

        if "|[" in self.regex[start_ind:]:
            or_start = self.regex[start_ind:].index("|[") + start_ind
        else:
            or_start = -1

        return or_start, start_ind

    def _handle_or_end(self, begin_nested, nested_ors, start_ind, or_end):
        nested_ors[begin_nested] = or_end
        start_ind = or_end + 2

        if "|[" in self.regex[start_ind:]:
            or_start = self.regex[start_ind:].index("|[") + start_ind
        else:
            or_start = -1

        or_end = self.regex[start_ind:].index("]|") + start_ind

        return or_start, or_end


    def _handle_zero_start(self, nested_zero_starts, zero_start, start_ind):
        nested_zero_starts.append(zero_start)
        start_ind = zero_start + 2

        if "*(" in self.regex[start_ind:]:
            zero_start = self.regex[start_ind:].index("*(") + start_ind
        else:
            zero_start = -1

        return zero_start, start_ind

    def _handle_zero_end(self, begin_nested, zeros, start_ind, zero_end):
        zeros[begin_nested] = zero_end
        start_ind = zero_end + 1

        if "*(" in self.regex[start_ind:]:
            zero_start = self.regex[start_ind:].index("*(") + start_ind
        else:
            zero_start = -1

        zero_end = self.regex[start_ind:].index(")") + start_ind

        return zero_start, zero_end

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
        start_ind = self.ind

        if "|[" in self.regex[start_ind:]:
            or_start = self.regex[start_ind:].index("|[") + start_ind
        else:
            or_start = -1

        or_end = self.regex[start_ind:].index("]|") + start_ind

        if "*(" in self.regex[start_ind:]:
            zero_start = self.regex[start_ind:].index("*(") + start_ind
            zero_end = self.regex[start_ind:].index(")") + start_ind
        else:
            zero_start = -1
            zero_end = -1

        if zero_start < zero_end or or_start < or_end:

            upcoming_nested_or = or_start != -1 and or_start < or_end
            upcoming_nested_zero = zero_start != -1 and zero_start < zero_end

            while upcoming_nested_or or upcoming_nested_zero or \
                  nested_or_starts or inner_zeros:

                if upcoming_nested_or or upcoming_nested_zero:

                    if upcoming_nested_or and upcoming_nested_zero:
                        if or_start < zero_start:
                            or_start, start_ind = self._handle_or_start(nested_or_starts,
                                                                        or_start, start_ind)
                        else:
                            zero_start, start_ind = self._handle_zero_start(nested_zero_starts,
                                                                            zero_start, start_ind)
                    elif upcoming_nested_or:
                        or_start, start_ind = self._handle_or_start(nested_or_starts,
                                                                    or_start, start_ind)
                    else:
                        zero_start, start_ind = self._handle_zero_start(nested_zero_starts,
                                                                        zero_start, start_ind)

                else:
                    if nested_zero_starts:
                        zero_next = nested_zero_starts[-1]
                    else:
                        zero_next = nested_or_starts[-1] + 1

                    if nested_or_starts:
                        or_next = nested_or_starts[-1]
                    else:
                        or_next = nested_zero_starts[-1] + 1

                    if zero_next < or_next:
                        begin_nested = nested_zero_starts.pop()
                        zero_start, zero_end = self._handle_zero_end(begin_nested, inner_zeros,
                                                                     start_ind, or_end)
                    else:
                        begin_nested = nested_or_starts.pop()
                        or_start, or_end = self._handle_or_end(begin_nested, nested_ors,
                                                               start_ind, or_end)

                upcoming_nested_or = or_start != -1 and or_start < or_end
                upcoming_nested_zero = zero_start != -1 and zero_start < zero_end

        if nested_or_starts:
            raise ParseError("Unmatched Or delimiters")

        alterns = split_inner_or(self.regex[self.ind:or_end], nested_ors, inner_zeros)

        self.ind = or_end
        self.consume("]")
        self.consume("|")

        return Or(list(map(lambda x: Parser(x).parse(), alterns)))

    def parse_zero_or_more(self):
        """
        Parse a ZeroOrMore starting at current index
        """

        self.consume("*")
        self.consume("(")

        zero_starts = []
        nested_zeros = {}
        start_ind = self.ind

        if "*(" in self.regex[start_ind:]:
            zero_start = self.regex[start_ind:].index("*(") + start_ind
        else:
            zero_start = -1

        zero_end = self.regex[start_ind:].index(")") + start_ind

        if zero_start < zero_end:
            while zero_start != -1 and zero_start < zero_end or zero_starts:
                if zero_start != -1 and zero_start < zero_end:
                    zero_start, start_ind = self._handle_zero_start(zero_starts, zero_start,
                                                                    start_ind)
                else:
                    begin_nested = zero_starts.pop()
                    zero_start, zero_end = self._handle_zero_end(begin_nested, nested_zeros,
                                                                 start_ind, zero_end)

        if zero_starts:
            raise ParseError("Unmatched ZeroOrMore delimiters")

        inner = self.regex[self.ind:zero_end]

        self.ind = zero_end
        self.consume(")")

        return ZeroOrMore(Parser(inner).parse())

def split_inner_or(exp, ors, zeros):
    """
    Break up inside of Or expression into a list for further parsing
    Commas/string end are the delimiters, except within nested expressions
    """

    start_ind = 0
    split = []

    explen = len(exp)
    iterator = iter(range(explen))
    for i in iterator:
        if exp[i] == "|":
            split.append(exp[i:ors[i+2]])
            iter_consume(iterator, ors[i+2] - i)
            start_ind = ors[i+2] + 1
        elif exp[i] == "*":
            split.append(exp[i:zeros[i+2]])
            iter_consume(iterator, zeros[i+2] - i)
            start_ind = zeros[i+2] + 1
        elif exp[i] == ",":
            split.append(exp[start_ind:i])
            start_ind = i + 1
        elif i == explen - 1:
            split.append(exp[start_ind:i+1])

    return split
