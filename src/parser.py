from src.compiler import *
from src.errors import UnexpectedToken, ParseError

class Parser:

    def __init__(self, inp):
        try:
            regex, word = inp.split(":")
        except:
            print("Incorrect input format")
            exit(1)

        self.regex = regex
        self.word = word

        self.ind = 0

    def advance(self):
        self.ind += 1

    def consume(self, letter):
        if not self.regex[self.ind] == letter:
            raise UnexpectedToken

        self.advance()

    def parseOr(self):
        self.consume("|")
        self.consume("[")

        nested = 0
        startind = self.ind

        print(self.regex[self.ind:])

        if "|[" in self.regex[self.ind:]:
            nextstart = self.regex[self.ind:].index("|[")
        else:
            nextstart = -1

        endind = self.regex[self.ind:].index("]|")
        print(endind)

        while nextstart != -1:
            if nextstart < endind:
                nested += 1
                startind = nextstart + 2 + self.ind

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[")
                else:
                    nextstart = -1

                endind = self.regex[startind:].index("]|")
            else:
                nested -= 1
                startind = endind + 2 + self.ind

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[")
                else:
                    nextstart = -1

                endind = self.regex[startind:].index("]|")

        if nested != 0:
            raise ParseError("Unmatched Or delimiters")

        inner = self.regex[self.ind:endind]

        print(inner)

        self.consume("]")
        self.consume("|")
