# vim: set fileencoding=utf-8 :
import unittest

from src.parser import Parser
from src.node import ExpressionNode as Node, ExpressionLeaf as Leaf
from tests.parser import ParserWrapper, run_expressions, line, graph


class TestParser(unittest.TestCase):
    def test_constructor(self):
        node = Node('+', Leaf(1), Leaf(4))
        self.assertEqual(ParserWrapper(Parser).run(['1 + 4']), node)

    def test_identifiers(self):
        run_expressions(Parser, [('a', Leaf('a'))])

    def test_graph(self):
        assert graph(Parser, '4a') == ("""
         *
        ╭┴╮
        4 a
        """).replace('\n        ', '\n')[1:-1]

    def test_line(self):
        self.assertEqual(line(Parser, '4-a'), '4 - a')

    def test_reset_after_failure(self):
        parser = ParserWrapper(Parser)
        parser.run(['-(3a+6b)'])
        possibilities1 = parser.parser.possibilities
        self.assertNotEqual(possibilities1, [])

        parser.run(['5+2*6'])
        possibilities2 = parser.parser.possibilities
        self.assertNotEqual(possibilities2, [])

        self.assertNotEqual(possibilities1, possibilities2)
