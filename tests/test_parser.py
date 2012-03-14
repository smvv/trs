# vim: set fileencoding=utf-8 :
import unittest

from src.parser import Parser
from src.node import ExpressionNode as Node, ExpressionLeaf as Leaf
from tests.parser import ParserWrapper, run_expressions, line, graph
from tests.rulestestcase import tree
from src.rules.goniometry import sin, cos
from src.rules.derivatives import der


class TestParser(unittest.TestCase):
    def test_constructor(self):
        node = Node('+', Leaf(1), Leaf(4))
        self.assertEqual(ParserWrapper(Parser).run(['1 + 4']), node)

    def test_identifiers(self):
        run_expressions(Parser, [('a', Leaf('a'))])

    def test_graph(self):
        self.assertEqual(graph(Parser, '4a'), ("""
         *
        ╭┴╮
        4 a
        """).replace('\n        ', '\n')[1:-1])

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

    def test_moved_negation(self):
        a, b = tree('a,b')

        self.assertEqual(tree('-ab'), (-a) * b)
        self.assertEqual(tree('-(ab)'), (-a) * b)
        self.assertEqual(tree('-a / b'), (-a) / b)
        self.assertEqual(tree('-(a / b)'), (-a) / b)

    def test_functions(self):
        x = tree('x')

        self.assertEqual(tree('sin x'), sin(x))
        self.assertEqual(tree('sin(x)'), sin(x))
        self.assertEqual(tree('sin x ^ 2'), sin(x) ** 2)
        self.assertEqual(tree('sin(x) ^ 2'), sin(x) ** 2)
        self.assertEqual(tree('sin (x) ^ 2'), sin(x) ** 2)
        self.assertEqual(tree('sin(x ^ 2)'), sin(x ** 2))
        self.assertEqual(tree('sin cos x'), sin(cos(x)))
        self.assertEqual(tree('sin cos x ^ 2'), sin(cos(x)) ** 2)

    def test_bracket_derivative(self):
        x = tree('x')

        self.assertEqual(tree('[x]\''), der(x))
        self.assertEqual(tree('[x]\'\''), der(der(x)))

    def test_bracket_derivative(self):
        exp, x, d = tree('x ^ 2, x, d')

        self.assertEqual(tree('d/dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d / dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d/dx x ^ 2 + x'), der(exp, x) + x)
        self.assertEqual(tree('d/dx (x ^ 2 + x)'), der(exp + x, x))
        self.assertEqual(tree('d/d'), d / d)
        # FIXME: self.assertEqual(tree('d(x ^ 2)/dx'), der(exp, x))
