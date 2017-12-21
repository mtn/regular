import unittest

from src.nodes import *
from src.compiler import *

class TestNodes(unittest.TestCase):
    """
    Tests functionality nodes
    """
    
    def test_simple_list(self):
        last = CharacterNode("c", EmptyString())
        middle = CharacterNode("b", last)
        first = CharacterNode("a", middle)

        self.assertTrue(isinstance(last.derive("c"), EmptyString))
        self.assertTrue(isinstance(last.derive("d"), NeverMatches))

        self.assertTrue(isinstance(middle.derive("b"), CharacterNode))
        self.assertTrue(isinstance(middle.derive("c"), NeverMatches))
        self.assertEqual(middle.derive("b"), last)

        self.assertTrue(isinstance(first.derive("a"), CharacterNode))
        self.assertTrue(isinstance(first.derive("b"), NeverMatches))
        self.assertEqual(first.derive("a"), middle)


    def test_list_with_alternation(self):
        last = CharacterNode("d", EmptyString())
        middle = AlternationNode([CharacterNode("b", last), CharacterNode("c", last)])
        first = CharacterNode("a", middle)

        self.assertTrue(isinstance(last.derive("d"), EmptyString))
        self.assertTrue(isinstance(last.derive("c"), NeverMatches))

        self.assertTrue(isinstance(middle.derive("b"), CharacterNode))
        self.assertTrue(isinstance(middle.derive("c"), CharacterNode))
        self.assertTrue(isinstance(middle.derive("a"), NeverMatches))
        self.assertEqual(middle.derive("b"), last)
        self.assertEqual(middle.derive("c"), last)

        self.assertTrue(isinstance(first.derive("a"), AlternationNode))
        self.assertTrue(isinstance(first.derive("b"), NeverMatches))
        self.assertEqual(first.derive("a"), middle)

    def test_multiple_alternations(self):
        last = CharacterNode("d", EmptyString())
        middle2 = AlternationNode([CharacterNode("b", last), CharacterNode("c", last)])
        middle1 = AlternationNode([CharacterNode("b", middle2), CharacterNode("c", middle2)])
        first = CharacterNode("a", middle1)

        self.assertTrue(last.canMatchMore())
        self.assertTrue(isinstance(last.derive("d"), EmptyString))
        self.assertTrue(isinstance(last.derive("c"), NeverMatches))

        self.assertTrue(middle2.canMatchMore())
        self.assertTrue(isinstance(middle2.derive("b"), CharacterNode))
        self.assertTrue(isinstance(middle2.derive("c"), CharacterNode))
        self.assertTrue(isinstance(middle2.derive("a"), NeverMatches))
        self.assertEqual(middle2.derive("b"), last)
        self.assertEqual(middle2.derive("c"), last)

        self.assertTrue(middle1.canMatchMore())
        self.assertTrue(isinstance(middle1.derive("b"), AlternationNode))
        self.assertTrue(isinstance(middle1.derive("c"), AlternationNode))
        self.assertTrue(isinstance(middle1.derive("a"), NeverMatches))
        self.assertEqual(middle1.derive("b"), middle2)
        self.assertEqual(middle1.derive("c"), middle2)

        self.assertTrue(first.canMatchMore())
        self.assertTrue(isinstance(first.derive("a"), AlternationNode))
        self.assertTrue(isinstance(first.derive("b"), NeverMatches))
        self.assertEqual(first.derive("a"), middle1)


    def test_any_character_node(self):

        any_node = AnyCharacterNode(EmptyString())

        self.assertTrue(isinstance(any_node.derive("a"), EmptyString))
        self.assertTrue(isinstance(any_node.derive("b"), EmptyString))

    def test_repetition_node(self):

        tail = CharacterNode("d", EmptyString())
        repetition = RepetitionNode(tail)
        repetition_body = CharacterNode("a", CharacterNode("b", CharacterNode(
            "c", repetition)))
        repetition.head = repetition_body

        self.assertTrue(isinstance(repetition.derive("a"), CharacterNode))
        self.assertTrue(isinstance(repetition.derive("d"), EmptyString))
        self.assertTrue(isinstance(repetition.derive("a").derive("b").derive("c"),
                                   RepetitionNode))

        self.assertEqual(repetition.derive("a").derive("b").derive("c"), repetition)
        self.assertEqual(repetition.derive("a").derive("b").derive("c").derive("a"),
                         repetition.derive("a"))


class TestCompiler(unittest.TestCase):
    """
    Tests for IR->linked list compiler
    """

    def test_zero_or_more_matches(self):
        """
        Tests for ZeroOrMore expression types
        """

        self.assertTrue(RE(ZeroOrMore("abc")).match("abcabc"))
        self.assertTrue(RE(ZeroOrMore("abc")).match("abc"))
        self.assertTrue(RE(ZeroOrMore("abc")).match(""))

    def test_concatentation(self):
        """
        Test for different concatentation combinations
        """

        # self.assertTrue(RE([ZeroOrMore("abc"), "d"]).match("d"))
        # self.assertTrue(RE(["a", Or(["a", "b"]), "d"]).match("abd"))

        pass
        # digit = Or(["0", "1"])
        # digit2 = Or(["2", "3"])

        # self.assertTrue(RE([digit, digit2]).match("1,2"))

        # phone_number = RE([Or([["(", digit, digit, digit, ") "], ""]), digit, digit, digit, "-", digit, digit, digit, digit])
        # print(phone_number.start)
        # print(phone_number.start.alternatives[0].next)
        # print(digit)

        # self.assertTrue(phone_number.match("(123) 456-7891"))
        # self.assertTrue(phone_number.match("123-4567"))
        # self.assertFalse(phone_number.match("55"))

        # self.assertFalse(RE(["a", Or(["a", "b"]), "d"]).match("aed"))

if __name__ == "__main__":
    unittest.main()
