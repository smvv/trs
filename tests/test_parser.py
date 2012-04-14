# vim: set fileencoding=utf-8 :
import unittest

from src.parser import Parser
from src.node import ExpressionNode as Node, ExpressionLeaf as Leaf, \
        SPECIAL_TOKENS, sin, cos, der, log, ln, integral, indef, absolute
from tests.parser import ParserWrapper, run_expressions, line, graph
from tests.rulestestcase import tree


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

    def test_binary(self):
        a, b, c = tree('a, b, c')

        self.assertEqual(tree('a ^^ b'), a & b)
        self.assertEqual(tree('a vv b'), a | b)
        self.assertEqual(tree('a vv b vv c'), (a | b) | c)
        self.assertEqual(tree('a vv b ^^ c'), a | (b & c))

    def test_preprocessor(self):
        self.assertEqual(tree('ab'), tree('a * b'))
        self.assertEqual(tree('abc'), tree('a * b * c'))
        self.assertEqual(tree('a2'), tree('a ^ 2'))
        self.assertEqual(tree('a 2'), tree('a * 2'))
        self.assertEqual(tree('2a'), tree('2 * a'))
        self.assertEqual(tree('2(a + b)'), tree('2 * (a + b)'))
        self.assertEqual(tree('(a + b)2'), tree('(a + b) * 2'))

        self.assertEqual(tree('(a)(b)'), tree('(a) * (b)'))
        self.assertEqual(tree('(a)[b]\''), tree('(a) * [b]\''))

        # FIXME: self.assertEqual(tree('(a)|b|'), tree('(a) * |b|'))
        # FIXME: self.assertEqual(tree('|a|(b)'), tree('|a| * (b)'))
        # FIXME: self.assertEqual(tree('a|b|'), tree('a * |b|'))
        # FIXME: self.assertEqual(tree('|a|b'), tree('|a| * b'))
        self.assertEqual(tree('|a||b|'), tree('|a| * |b|'))

    def test_functions(self):
        x = tree('x')

        self.assertEqual(tree('sin x'), sin(x))
        self.assertEqual(tree('sin 2 x'), sin(2) * x)  # FIXME: correct?
        self.assertEqual(tree('sin x ^ 2'), sin(x ** 2))
        self.assertEqual(tree('sin(x) ^ 2'), sin(x) ** 2)
        self.assertEqual(tree('sin(x ^ 2)'), sin(x ** 2))

        self.assertEqual(tree('sin cos x'), sin(cos(x)))
        self.assertEqual(tree('sin cos x ^ 2'), sin(cos(x ** 2)))
        self.assertEqual(tree('sin cos(x) ^ 2'), sin(cos(x) ** 2))

    def test_bracket_derivative(self):
        x = tree('x')

        self.assertEqual(tree('[x]\''), der(x))
        self.assertEqual(tree('[x]\'\''), der(der(x)))

    def test_delta_derivative(self):
        exp, x, d = tree('x ^ 2, x, d')

        self.assertEqual(tree('d/dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d / dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d/dx x ^ 2 + x'), der(exp + x, x))
        self.assertEqual(tree('(d/dx x ^ 2) + x'), der(exp, x) + x)
        self.assertEqual(tree('d/d'), d / d)
        # FIXME: self.assertEqual(tree('d(x ^ 2)/dx'), der(exp, x))

    def test_logarithm(self):
        x, g = tree('x, g')

        self.assertEqual(tree('log(x, e)'), ln(x))
        self.assertEqual(tree('log(x, 10)'), log(x))
        self.assertEqual(tree('log(x, 2)'), log(x, 2))
        self.assertEqual(tree('log(x, g)'), log(x, g))

        self.assertEqual(tree('log_2(x)'), log(x, 2))
        self.assertEqual(tree('log_10(x)'), log(x))
        self.assertEqual(tree('log_g(x)'), log(x, g))
        self.assertEqual(tree('log_g x'), log(x, g))

    def test_special_tokens(self):
        for token in SPECIAL_TOKENS:
            self.assertEqual(tree(token), Leaf(token))
            a, t = Leaf('a'), Leaf(token)
            self.assertEqual(tree('a' + token), a * t)
            # FIXME: self.assertEqual(tree('a' + token + 'a'), a * t * a)

    def test_integral(self):
        x, y, dx, a, b, l2 = tree('x, y, dx, a, b, 2')

        self.assertEqual(tree('int x'), integral(x, x))
        self.assertEqual(tree('int x2'), integral(x ** 2, x))
        self.assertEqual(tree('int x2 dx'), integral(x ** 2, x))
        self.assertEqual(tree('int x2 dy'), integral(x ** 2, y))

        self.assertEqual(tree('int_a^b x2'), integral(x ** 2, x, a, b))
        self.assertEqual(tree('int_a^b x2 dy'), integral(x ** 2, y, a, b))
        self.assertEqual(tree('int_(a-b)^(a+b) x2'),
                         integral(x ** 2, x, a - b, a + b))

        self.assertEqual(tree('int_a^b 2x'), integral(l2 * x, x, a, b))
        self.assertEqual(tree('int_a^b2 x'), integral(x, x, a, b ** 2))

    def test_indefinite_integral(self):
        x2, a, b = tree('x ^ 2, a, b')

        self.assertEqual(tree('[x ^ 2]_a^b'), indef(x2, a, b))

    def test_absolute_value(self):
        x = tree('x')

        self.assertEqual(tree('|x|'), absolute(x))
        self.assertEqual(tree('|x2|'), absolute(x ** 2))
