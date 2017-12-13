"""
Regex linked-list node type definitions
"""

class RegexNode:
    """
    Base node type
    """

    def derive(self, char):
        return NeverMatches

NeverMatches = RegexNode()
EmptyString = RegexNode()

class CharacterNode(RegexNode):

    def __init__(self, char, next_node):
        self.char = char
        self.next = next_node

    def derive(self, char):
        if char == self.char:
            return self.next
        return NeverMatches

class AlternationNode(RegexNode):

    def __new__(self, alternatives):
        _alternatives = list(filter(lambda x: x != NeverMatches, alternatives))
        if not _alternatives:
            return NeverMatches
        elif len(_alternatives) == 1:
            return _alternatives[0]

        self.alternatives = _alternatives
        return self

    def derive(self, char):
        return AlternationNode(list(map(lambda x: x.derive(char), self.alternatives)))
