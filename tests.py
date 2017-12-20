import unittest

from src.compiler import *

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

        self.assertTrue(RE([ZeroOrMore("abc"), "d"]).match("d"))
        self.assertTrue(RE(["a", Or(["a", "b"]), "d"]).match("abd"))

        digit = Or(["0", "1", "3", "4", "5", "6", "7", "8", "9"])
        phone_number = RE([Or([["(", digit, digit, digit, ") "], ""]), digit, digit,
                           digit, "-", digit, digit, digit, digit])

        self.assertTrue(phone_number.match("(415) 555-1212"))
        self.assertTrue(phone_number.match("555-1212"))
        self.assertFalse(phone_number.match("55"))

        self.assertFalse(RE(["a", Or(["a", "b"]), "d"]).match("aed"))

if __name__ == "__main__":
    unittest.main()
