"""
Regex linked-list node type definitions
"""

class RegexNode:
    """
    Base node type
    """

    def __new__(cls, *args, **kwargs):

        if not args:
            return super(RegexNode, cls).__new__(cls)

        elif len(args) == 1:

            # List of alternatives -> AlternationNode
            if isinstance(args[0], list):
                _alternatives = list(filter(lambda x: not isinstance(x, NeverMatches), args[0]))

                if not _alternatives:
                    return NeverMatches()
                elif len(_alternatives) == 1:
                    return _alternatives[0]

                alternode = super(RegexNode, cls).__new__(AlternationNode)
                alternode.__init__(_alternatives)
                return alternode

            else:
                return super(RegexNode, cls).__new__(cls)

        # Character and next -> CharacterNode
        elif len(args) == 2:
            return super(RegexNode, cls).__new__(CharacterNode)

    def derive(self, _):
        return NeverMatches()

    def matchEnd(self):
        return False

    def canMatchMore(self):
        return not self.matchEnd()

    def __repr__(self):
        return "RegexNode"

class NeverMatches(RegexNode):
    def __repr__(self):
        return "NeverMatches"

class EmptyString(RegexNode):
    def matchEnd(self):
        return True

    def __repr__(self):
        return "EmptyString"

class CharacterNode(RegexNode):

    def __init__(self, char, next_node):
        self.char = char
        self.next = next_node

    def derive(self, char):
        if char == self.char:
            return self.next
        return NeverMatches()

    def __repr__(self):
        return "CharNode({})".format(self.char)

class AlternationNode(RegexNode):

    def __init__(self, alternatives):
        self.alternatives = alternatives

    def derive(self, char):
        return AlternationNode(list(map(lambda c: c.derive(char), self.alternatives)))

    def matchEnd(self):
        if [altern for altern in self.alternatives if altern.matchEnd()]:
            return True
        return False

    def canMatchMore(self):
        if [altern for altern in self.alternatives if altern.canMatchMore()]:
            return True
        return False

    def __repr__(self):
        return "Alternode({})".format(self.alternatives)

class AnyCharacterNode(RegexNode):

    def __init__(self, next_node):
        self.next = next_node

    def derive(self, _):
        return self.next

    def __repr__(self):
        return "AnyNode"


class RepetitionNode(RegexNode):

    def __init__(self, next_node):
        self.head = NeverMatches()
        self.next = next_node

    def derive(self, char):
        return AlternationNode([
            self.head.derive(char),
            self.next.derive(char)
            ])

    def matchEnd(self):
        return self.next.matchEnd()

    def canMatchMore(self):
        return True

    def __repr__(self):
        return "RepNode(head: {}, next: {})".format(self.head, self.next)
