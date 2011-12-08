import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L
from src.match import patterns, matches
from src.parser import Parser

from tests.parser import ParserWrapper


class TestMatch(unittest.TestCase):
    def setUp(self):
        self.parser = ParserWrapper(Parser)

    def test_constant(self):
        pass

    def assert_matches(self, exp, pattern_name):
        self.assertTrue(matches(self.parser.run([exp]), patterns[pattern_name]))
