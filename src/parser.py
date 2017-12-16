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
            raise UnexpectedToken(letter, self.regex[self.ind])

        self.advance()

    def parseOr(self):
        self.consume("|")
        self.consume("[")

        nested = 0
        startind = self.ind

        print(self.regex[startind:])
        if "|[" in self.regex[self.ind:]:
            nextstart = self.regex[self.ind:].index("|[") + self.ind
        else:
            nextstart = -1

        endind = self.regex[self.ind:].index("]|") + self.ind

        counter = 0
        while nextstart != -1 or nested:
            counter += 1
            if nextstart != -1 and nextstart < endind:
                nested += 1
                startind = nextstart + 2

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[") + startind
                else:
                    nextstart = -1
            else:
                nested -= 1
                startind = endind + 2

                if "|[" in self.regex[startind:]:
                    nextstart = self.regex[startind:].index("|[") + startind
                else:
                    nextstart = -1
                print(nextstart)

                endind = self.regex[startind:].index("]|") + startind


        if nested != 0:
            raise ParseError("Unmatched Or delimiters")

        inner = self.regex[self.ind:endind]
        print("inner {}".format(inner))

        self.ind = endind
        self.consume("]")
        self.consume("|")
