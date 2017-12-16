
class UnexpectedToken(Exception):
    def __init__(self, expected, given):
        self.message = "Expected {}, given {}".format(expected, given)

class ParseError(Exception):
    def __init__(self, msg):
        self.message = msg
