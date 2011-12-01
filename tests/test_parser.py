# vim: set fileencoding=utf-8 :
import unittest

from external.graph_drawing.graph import generate_graph
from external.graph_drawing.line import generate_line

from src.parser import Parser
from src.node import ExpressionNode as Node, ExpressionLeaf as Leaf
from tests.parser import ParserWrapper, run_expressions


def graph(*exp, **kwargs):
    return generate_graph(ParserWrapper(Parser, **kwargs).run(exp))


def line(*exp, **kwargs):
    return generate_line(ParserWrapper(Parser, **kwargs).run(exp))


class TestParser(unittest.TestCase):
    def test_constructor(self):
        node = Node('+', Leaf(1), Leaf(4))
        self.assertEqual(ParserWrapper(Parser).run(['1 + 4']), node)

    def test_identifiers(self):
        run_expressions(Parser, [('a', Leaf('a'))])

    def test_graph(self):
        assert graph('4a') == ("""
         *
        ╭┴╮
        4 a
        """).replace('\n        ', '\n')[1:-1]

    def test_line(self):
        self.assertEqual(line('4a'), '4 * a')
