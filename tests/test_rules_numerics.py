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
from src.rules.numerics import match_add_numerics, add_numerics, \
        match_divide_numerics, divide_numerics, reduce_fraction_constants, \
        match_multiply_numerics, multiply_numerics, multiply_zero, \
        multiply_one, raise_numerics
from src.node import ExpressionLeaf as L, Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNumerics(RulesTestCase):

    def test_match_add_numerics(self):
        l1, l2 = root = tree('1 + 2')
        possibilities = match_add_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (Scope(root), l1, l2))])

        (l1, b), l2 = root = tree('1 + b + 2')
        possibilities = match_add_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (Scope(root), l1, l2))])

    def test_add_numerics(self):
        l1, l2 = root = tree('1 + 2')
        self.assertEqual(add_numerics(root, (Scope(root), l1, l2)), 3)

        (l1, a), l2 = root = tree('1 + a + 2')
        self.assertEqual(add_numerics(root, (Scope(root), l1, l2)), L(3) + a)

    def test_add_numerics_negations(self):
        ml1, l2 = root = tree('-1 + 2')
        self.assertEqual(add_numerics(root, (Scope(root), ml1, l2)), 1)
        l1, ml2 = root = tree('1 - 2')
        self.assertEqual(add_numerics(root, (Scope(root), l1, ml2)), -1)

    def test_match_divide_numerics(self):
        a, b, i2, i3, i4, i6, f1, f2, f3 = tree('a,b,2,3,4,6,1.0,2.0,3.0')

        root = i6 / i2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities, [P(root, divide_numerics)])

        root = -i6 / i2
        self.assertEqualPos(match_divide_numerics(root), [])

        root = i6 / -i2
        self.assertEqualPos(match_divide_numerics(root), [])

        root = i2 / i4
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, reduce_fraction_constants, (2,))])

        root = f3 / i2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = i3 / f2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = f3 / f2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = i3 / f1
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = a / b
        self.assertEqualPos(match_divide_numerics(root), [])

    def test_divide_numerics(self):
        i2, i3, i6, f2, f3 = tree('2,3,6,2.0,3.0')

        self.assertEqual(divide_numerics(i6 / i2, ()), 3)
        self.assertEqual(divide_numerics(f3 / i2, ()), 1.5)
        self.assertEqual(divide_numerics(i3 / f2, ()), 1.5)
        self.assertEqual(divide_numerics(f3 / f2, ()), 1.5)
        self.assertEqual(divide_numerics(-(i6 / i2), ()), -i3)

    def test_reduce_fraction_constants(self):
        l1, l2 = tree('1,2')
        self.assertEqual(reduce_fraction_constants(l2 / 4, (2,)), l1 / l2)

    #def test_fraction_to_int_fraction(self):
    #    l1, l4 = tree('1,4')
    #    self.assertEqual(fraction_to_int_fraction(l4 / 3, (1, 1, 3)),
    #                     l1 + l1 / 3)

    def test_match_multiply_numerics(self):
        i2, i3, i6, f2, f3, f6 = tree('2,3,6,2.0,3.0,6.0')

        root = i3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), i3, i2))])

        root = f3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), f3, i2))])

        root = i3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), i3, f2))])

        root = f3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), f3, f2))])

    def test_match_multiply_zero(self):
        l0, x = root = tree('0x')
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_zero, (l0,))])

    def test_match_multiply_one(self):
        l1, x = root = tree('1x')
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_one, (Scope(root), l1))])

        (x, l1), x = root = tree('x * 1x')
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_one, (Scope(root), l1))])

    def test_multiply_numerics(self):
        a, b, i2, i3, i6, f2, f3, f6 = tree('a,b,2,3,6,2.0,3.0,6.0')

        i3, i2 = root = tree('3 * 2')
        self.assertEqual(multiply_numerics(root, (Scope(root), i3, i2)), 6)
        f3, i2 = root = tree('3.0 * 2')
        self.assertEqual(multiply_numerics(root, (Scope(root), f3, i2)), 6.0)
        i3, f2 = root = tree('3 * 2.0')
        self.assertEqual(multiply_numerics(root, (Scope(root), i3, f2)), 6.0)
        f3, f2 = root = tree('3.0 * 2.0')
        self.assertEqual(multiply_numerics(root, (Scope(root), f3, f2)), 6.0)

        ((a, i3), i2), b = root = tree('a * 3 * 2 * b')
        self.assertEqualNodes(multiply_numerics(root,
                              (Scope(root), i3, i2)), a * 6 * b)

    def test_multiply_numerics_negation(self):
        l1_neg, l2 = root = tree('-1 * 2')
        self.assertEqualNodes(multiply_numerics(root, (Scope(root), l1_neg,
                                                      l2)), -l2)

        root, l6 = tree('1 + -2 * 3,6')
        l1, mul = root
        l2_neg, l3 = mul
        self.assertEqualNodes(multiply_numerics(mul, (Scope(mul),
                                                      l2_neg, l3)), -l6)

        root, l30 = tree('-5 * x ^ 2 - -15x - 5 * 6,30')
        rest, mul = root
        l5_neg, l6 = mul
        self.assertEqualNodes(multiply_numerics(mul, (Scope(mul),
                                                      l5_neg, l6)), -l30)

    def test_raise_numerics(self):
        l1, l2 = root = tree('2 ^ 3')
        self.assertEqualNodes(raise_numerics(root, (l1, l2, 0)), L(8))

        l1_neg, l2 = root = tree('(-2) ^ 2')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2, 0)), --L(4))

        l1_neg, l2 = root = tree('(-2) ^ 3')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2, 0)), ---L(8))

        l1_neg, l2 = root = tree('-((-2) ^ 3)')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2, 1)), ----L(8))

        l1_neg, l2 = root = tree('-(2 ^ 3)')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2, 1)), -L(8))
