import unittest

from src.nodes import *
from src.compiler import *
from src.parser import *

class TestNodes(unittest.TestCase):
    """
    Tests functionality nodes
    """
    def test_simple_dfa(self):
        """
        Test to ensure a DFA gets derived correctly
        """

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


    def test_dfa_with_alternation(self):
        """
        Test to ensure a single alternation in a DFA gets derived correctly
        """

        last = CharacterNode("d", EmptyString())
        middle = AlternationFactory([CharacterNode("b", last), CharacterNode("c", last)])
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
        """
        Test that a DFA including more than one alternation is gets derived correctly
        """

        last = CharacterNode("d", EmptyString())
        middle2 = AlternationFactory([CharacterNode("b", last), CharacterNode("c", last)])
        middle1 = AlternationFactory([CharacterNode("b", middle2), CharacterNode("c", middle2)])
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
        """
        Ensure the AnyCharacter node advances given any input character
        """

        any_node = AnyCharacterNode(EmptyString())

        self.assertTrue(isinstance(any_node.derive("a"), EmptyString))
        self.assertTrue(isinstance(any_node.derive("b"), EmptyString))

    def test_repetition_node(self):
        """
        Basic checks to ensure the repetition node is circular, etc.
        """

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
    Tests IR->DFA (compiler)
    """

    pass

class TestMatch(unittest.TestCase):
    """
    Test IR->RE.match matches correctly
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

        self.assertTrue(RE([]).match(""))

        self.assertTrue(RE([ZeroOrMore("abc"), "d"]).match("d"))
        self.assertTrue(RE(["a", Or(["a", "b"]), "d"]).match("abd"))
        self.assertFalse(RE(["a", Or(["a", "b"]), "d"]).match("aed"))


        digit = Or(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

        self.assertTrue(RE([digit, digit]).match("12"))

        phone_number = RE([Or([["(", digit, digit, digit, ")", " "], ""]), digit, digit,
                           digit, "-", digit, digit, digit, digit])

        self.assertTrue(phone_number.match("(123) 456-7891"))
        self.assertTrue(phone_number.match("123-4567"))
        self.assertFalse(phone_number.match("55"))


class TestParser(unittest.TestCase):
    """
    Assumes IR match works correctly and tests match from raw input
    """

    # api: RE(Parser(line).parse()).match(...)
    def test_simple_nonnested_concatenation(self):
        self.assertTrue(RE(Parser("abc").parse()).match("abc"))
        self.assertFalse(RE(Parser("abc").parse()).match("abd"))

        self.assertTrue(RE([]).match(""))
        self.assertTrue(RE(Parser("").parse()).match(""))
        self.assertFalse(RE(Parser("").parse()).match("abd"))

        self.assertTrue(RE(Parser("_").parse()).match("a"))
        self.assertTrue(RE(Parser("_").parse()).match("b"))
        self.assertFalse(RE(Parser("_").parse()).match("bc"))

        self.assertTrue(RE(Parser("__").parse()).match("ab"))
        self.assertFalse(RE(Parser("__").parse()).match("abc"))

        self.assertTrue(RE(Parser("a|[b,c,de]|f").parse()).match("abf"))
        self.assertTrue(RE(Parser("a|[b,c,de]|f").parse()).match("acf"))
        self.assertTrue(RE(Parser("a|[b,c,de]|f").parse()).match("adef"))
        self.assertFalse(RE(Parser("a|[b,c,de]|f").parse()).match("aef"))

        self.assertTrue(RE(Parser("a*(de)f").parse()).match("af"))
        self.assertTrue(RE(Parser("a*(de)f").parse()).match("adef"))
        self.assertTrue(RE(Parser("a*(de)f").parse()).match("adedef"))

    def test_complex_nonnested_concatenation(self):
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("abf"))
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("acf"))
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("abdef"))
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("acdef"))
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("abdedef"))
        self.assertTrue(RE(Parser("a|[b,c]|*(de)f").parse()).match("acdedef"))

        self.assertTrue(RE(Parser("a_|[b,c]|*(de)f").parse()).match("abcdedef"))

    def test_simple_nested(self):
        self.assertTrue(RE(Parser("|[b,|[c,def]|,de]|").parse()).match("def"))
        self.assertTrue(RE(Parser("|[b,|[c,def]|,de]|").parse()).match("c"))
        self.assertTrue(RE(Parser("|[b,|[c,def]|,de]|").parse()).match("b"))
        self.assertTrue(RE(Parser("|[b,|[c,def]|,de]|").parse()).match("de"))

        self.assertTrue(RE(Parser("*(b*(cdef)de)").parse()).match(""))
        self.assertTrue(RE(Parser("*(b*(cdef)de)").parse()).match("bde"))
        self.assertTrue(RE(Parser("*(b*(cdef)de)").parse()).match("bcdefde"))
        self.assertTrue(RE(Parser("*(b*(cdef)de)").parse()).match("bcdefcdefde"))

        self.assertTrue(RE(Parser("|[b,*(cdef),de]|").parse()).match("b"))
        self.assertTrue(RE(Parser("|[b,*(cdef),de]|").parse()).match("de"))
        self.assertTrue(RE(Parser("|[b,*(cdef),de]|").parse()).match(""))
        self.assertTrue(RE(Parser("|[b,*(cdef),de]|").parse()).match("cdef"))
        self.assertTrue(RE(Parser("|[b,*(cdef),de]|").parse()).match("cdefcdef"))

        self.assertTrue(RE(Parser("*(b|[c,def]|de)").parse()).match(""))
        self.assertTrue(RE(Parser("*(b|[c,def]|de)").parse()).match("bcde"))
        self.assertTrue(RE(Parser("*(b|[c,def]|de)").parse()).match("bdefde"))
        self.assertTrue(RE(Parser("*(b|[c,def]|de)").parse()).match("bcdebcde"))
        self.assertTrue(RE(Parser("*(b|[c,def]|de)").parse()).match("bdefdebdefde"))

    def test_nested_concatenation(self):
        self.assertTrue(RE(Parser("a|[b,|[c,def]|,de]|f").parse()).match("adeff"))
        self.assertTrue(RE(Parser("a|[b,|[c,def]|,de]|f").parse()).match("acf"))
        self.assertTrue(RE(Parser("a|[b,|[c,def]|,de]|f").parse()).match("abf"))
        self.assertTrue(RE(Parser("a|[b,|[c,def]|,de]|f").parse()).match("adef"))

        self.assertTrue(RE(Parser("a*(b*(cdef)de)f").parse()).match("af"))
        self.assertTrue(RE(Parser("a*(b*(cdef)de)f").parse()).match("abdef"))
        self.assertTrue(RE(Parser("a*(b*(cdef)de)f").parse()).match("abcdefdef"))
        self.assertTrue(RE(Parser("a*(b*(cdef)de)f").parse()).match("abcdefcdefdef"))

        self.assertTrue(RE(Parser("a|[b,*(cdef),de]|f").parse()).match("abf"))
        self.assertTrue(RE(Parser("a|[b,*(cdef),de]|f").parse()).match("adef"))
        self.assertTrue(RE(Parser("a|[b,*(cdef),de]|f").parse()).match("af"))
        self.assertTrue(RE(Parser("a|[b,*(cdef),de]|f").parse()).match("acdeff"))
        self.assertTrue(RE(Parser("a|[b,*(cdef),de]|f").parse()).match("acdefcdeff"))

        self.assertTrue(RE(Parser("a*(b|[c,def]|de)f").parse()).match("af"))
        self.assertTrue(RE(Parser("a*(b|[c,def]|de)f").parse()).match("abcdef"))
        self.assertTrue(RE(Parser("a*(b|[c,def]|de)f").parse()).match("abdefdef"))
        self.assertTrue(RE(Parser("a*(b|[c,def]|de)f").parse()).match("abcdebcdef"))
        self.assertTrue(RE(Parser("a*(b|[c,def]|de)f").parse()).match("abdefdebdefdef"))

if __name__ == "__main__":
    unittest.main()
