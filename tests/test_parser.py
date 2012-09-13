# vim: set fileencoding=utf-8 :
# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
from src.parser import Parser, find_possibilities
from src.node import ExpressionNode as Node, ExpressionLeaf as Leaf, \
        SPECIAL_TOKENS, sin, cos, der, log, ln, integral, indef, absolute, \
        Scope
from src.possibilities import Possibility as P
from src.rules.numerics import add_numerics
from tests.parser import ParserWrapper, run_expressions, line, graph
from tests.rulestestcase import RulesTestCase, tree


class TestParser(RulesTestCase):
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
        parser.parser.find_possibilities()
        possibilities1 = parser.parser.possibilities
        self.assertNotEqual(possibilities1, [])

        parser.run(['5+2*6'])
        parser.parser.find_possibilities()
        possibilities2 = parser.parser.possibilities
        self.assertNotEqual(possibilities2, [])

        self.assertNotEqual(possibilities1, possibilities2)

    def test_binary(self):
        a, b, c = tree('a, b, c')

        self.assertEqual(tree('a ^^ b'), a & b)
        self.assertEqual(tree('a vv b'), a | b)
        self.assertEqual(tree('a vv b vv c'), (a | b) | c)
        self.assertEqual(tree('a vv b ^^ c'), a | (b & c))

        self.assertEqual(tree('a & b'), a & b)
        self.assertEqual(tree('a vv b & c'), a | (b & c))

    def test_preprocessor(self):
        self.assertEqual(tree('ab'), tree('a * b'))
        self.assertEqual(tree('abc'), tree('a * b * c'))
        self.assertEqual(tree('a2'), tree('a * 2'))
        self.assertEqual(tree('a 2'), tree('a * 2'))
        self.assertEqual(tree('2a'), tree('2 * a'))
        self.assertEqual(tree('2(a + b)'), tree('2 * (a + b)'))
        self.assertEqual(tree('(a + b)2'), tree('(a + b) * 2'))

        self.assertEqual(tree('(a)(b)'), tree('a * b'))
        self.assertEqual(tree('(a)[b]'), tree('a * b'))
        self.assertEqual(tree('[a](b)'), tree('a * b'))
        self.assertEqual(tree('[a][b]'), tree('a * b'))

        # FIXME: self.assertEqual(tree('(a)|b|'), tree('(a) * |b|'))
        # FIXME: self.assertEqual(tree('|a|(b)'), tree('|a| * (b)'))
        # FIXME: self.assertEqual(tree('a|b|'), tree('a * |b|'))
        # FIXME: self.assertEqual(tree('|a|b'), tree('|a| * b'))
        self.assertEqual(tree('|a||b|'), tree('|a| * |b|'))

        self.assertEqual(tree('pi2'), tree('pi * 2'))

    def test_functions(self):
        x = tree('x')

        self.assertEqual(tree('sin x'), sin(x))
        self.assertEqual(tree('sin 2 x'), sin(2) * x)  # FIXME: correct?
        self.assertEqual(tree('sin x ^ 2'), sin(x ** 2))
        self.assertEqual(tree('sin^2 x'), sin(x) ** 2)
        self.assertEqual(tree('sin(x ^ 2)'), sin(x ** 2))

        self.assertEqual(tree('sin cos x'), sin(cos(x)))
        self.assertEqual(tree('sin cos x ^ 2'), sin(cos(x ** 2)))
        self.assertEqual(tree('sin cos(x) ^ 2'), sin(cos(x ** 2)))
        self.assertEqual(tree('sin (cos x) ^ 2'), sin(cos(x) ** 2))

    def test_brackets(self):
        self.assertEqual(*tree('[x], x'))
        self.assertEqual(*tree('[x], (x)'))
        self.assertEqual(*tree('[x ^ 2], x ^ 2'))
        self.assertEqual(*tree('[x ^ 2](x), x ^ 2 * x'))

        self.assertEqual(*tree('{x}, x'))
        self.assertEqual(*tree('{x ^ 2}, x ^ 2'))

    def test_derivative(self):
        x = tree('x')

        self.assertEqual(tree('[x]\''), der(x))
        self.assertEqual(tree('x\''), der(x))
        self.assertEqual(tree('[x]\'\''), der(der(x)))
        self.assertEqual(tree('(x)\'\''), der(der(x)))
        self.assertEqual(tree('x\'\''), der(der(x)))

    def test_delta_derivative(self):
        exp, x, d = tree('x ^ 2, x, d')

        self.assertEqual(tree('d/dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d / dx x ^ 2'), der(exp, x))
        self.assertEqual(tree('d/dx x ^ 2 + x'), der(exp, x) + x)
        self.assertEqual(tree('d/dx (x ^ 2 + x)'), der(exp + x, x))
        self.assertEqual(tree('d/d'), d / d)

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
            self.assertEqual(tree('a' + token + 'a'), a * t * a)

    def test_integral(self):
        x, y, dx, a, b, l2, oo = tree('x, y, dx, a, b, 2, oo')

        self.assertEqual(tree('int x'), integral(x, x))
        self.assertEqual(tree('int x ^ 2'), integral(x ** 2, x))
        self.assertEqual(tree('int x ^ 2 dx'), integral(x ** 2, x))
        self.assertEqual(tree('int x ^ 2 dy'), integral(x ** 2, y))

        self.assertEqual(tree('int_a^b x ^ 2'), integral(x ** 2, x, a, b))
        self.assertEqual(tree('int_a^b x ^ 2 dy'), integral(x ** 2, y, a, b))
        self.assertEqual(tree('int_(a-b)^(a+b) x ^ 2'),
                         integral(x ** 2, x, a - b, a + b))

        self.assertEqual(tree('int_a^b 2x'), integral(l2 * x, x, a, b))
        self.assertEqual(tree('int_a^b^2 x'), integral(x, x, a, b ** 2))
        self.assertEqual(tree('int_a^(b2) x'), integral(x, x, a, b * 2))

        self.assertEqual(tree('int x ^ 2 + 1'), integral(x ** 2, x) + 1)

        self.assertEqual(tree('int_a^b x ^ 2 dx'), integral(x ** 2, x, a, b))
        self.assertEqual(tree('int_a x ^ 2 dx'), integral(x ** 2, x, a, oo))

        self.assertEqual(tree('int_(-a)^b x dx'), integral(x, x, -a, b))
        self.assertEqual(tree('int_-a^b x^2 dx'), integral(x ** 2, x, -a, b))

    def test_indefinite_integral(self):
        x2, a, b, oo, l2 = tree('x ^ 2, a, b, oo, 2')

        self.assertEqual(tree('(x ^ 2)_a'), indef(x2, a, oo))
        self.assertEqual(tree('(x ^ 2)_a^b'), indef(x2, a, b))
        self.assertEqual(tree('(x ^ 2)_-a^b'), indef(x2, -a, b))
        self.assertEqual(tree('(x ^ 2)_-a^-b'), indef(x2, -a, -b))
        self.assertNotEqual(tree('(x ^ 2)_-2a^b'), indef(x2, -(l2 * a), b))
        self.assertEqual(tree('(x ^ 2)_(-2a)^b'), indef(x2, -(l2 * a), b))

    def test_absolute_value(self):
        x = tree('x')

        self.assertEqual(tree('|x|'), absolute(x))
        self.assertEqual(tree('|x2|'), absolute(x * 2))

    def test_find_possibilities_basic(self):
        l1, l2 = root = tree('1 + 2')
        self.assertEqual(find_possibilities(root),
                [P(root, add_numerics, (Scope(root), l1, l2))])

    def test_find_possibilities_duplicates(self):
        (l1, l2), l3 = root = tree('1 + 2 + 3')
        self.assertEqual(find_possibilities(root),
                [P(root, add_numerics, (Scope(root), l1, l2)),
                 P(root, add_numerics, (Scope(root), l1, l3)),
                 P(root, add_numerics, (Scope(root), l2, l3))])

    def test_no_expression_error(self):
        self.assertRaises(RuntimeError, ParserWrapper(Parser).run, ['', '?'])

    def test_precedence(self):
        self.assertEqual(tree('ab / cd'), tree('a * (b / c) * d'))

    def test_pi_multiplication_sign(self):
        self.assertEqual(tree('apia'), tree('a * pi * a'))
