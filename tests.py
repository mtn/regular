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
        self.assertEqual(middle.derive("b"), last)



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
