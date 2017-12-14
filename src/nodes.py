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

        # Alternation Node
        elif len(args) == 1:
            _alternatives = list(filter(lambda x: not isinstance(x, NeverMatches), args[0]))

            if not _alternatives:
                return NeverMatches()
            elif len(_alternatives) == 1:
                return _alternatives[0]

            alternode = super(RegexNode, cls).__new__(AlternationNode)
            alternode.__init__(_alternatives)
            return alternode


        elif len(args) == 2:
            charnode = super(RegexNode, cls).__new__(CharacterNode)
            charnode.__init__(args[0], args[1])
            return charnode

    def derive(self, _):
        return NeverMatches()

    def __repr__(self):
        return "RegexNode"

class NeverMatches(RegexNode):
    def __repr__(self):
        return "NeverMatches"

class EmptyString(RegexNode):
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

    def __repr__(self):
        return "Alternode({})".format(self.alternatives)

commonTail = CharacterNode('d',EmptyString())
alternation = AlternationNode([CharacterNode('b',commonTail),CharacterNode('c',commonTail)])
head = CharacterNode('a', alternation)

print(head.derive('a').derive('b'))
print(head.derive('a').derive('e'))
print(head.derive('a').derive('b').derive('d'))
