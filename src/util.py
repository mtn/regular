from itertools import islice
import collections


class UnexpectedToken(Exception):
    def __init__(self, expected, given):
        self.message = "Expected {}, given {}".format(expected, given)

class ParseError(Exception):
    def __init__(self, msg):
        self.message = msg


def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    if n is None:
        collections.deque(iterator, maxlen=0)
    else:
        next(islice(iterator, n, n), None)
