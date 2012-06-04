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
from src.rules.lineq import match_move_term, swap_sides, subtract_term, \
        divide_term, multiply_term, split_absolute_equation, \
        match_multiple_equations, substitute_variable, match_double_case, \
        double_case
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesLineq(RulesTestCase):

    def test_match_move_term_swap(self):
        root = tree('x = b')
        self.assertEqualPos(match_move_term(root), [])

        root = tree('a = bx')
        self.assertEqualPos(match_move_term(root), [P(root, swap_sides)])

    def test_match_move_term_subtract(self):
        root, a = tree('x + a = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, subtract_term, (a,))])

        root, cx = tree('x = b + cx, cx')
        self.assertEqualPos(match_move_term(root),
                [P(root, subtract_term, (cx,))])

    def test_match_move_term_divide(self):
        root, a = tree('ax = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, divide_term, (a,))])

    def test_match_move_term_multiply(self):
        root, a = tree('x / a = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, multiply_term, (a,))])

        root, x = tree('a / x = b, x')
        self.assertEqualPos(match_move_term(root),
                [P(root, multiply_term, (x,))])

        root, l1 = tree('-x = b, -1')
        self.assertEqualPos(match_move_term(root),
                [P(root, multiply_term, (l1,))])

    def test_match_move_term_absolute(self):
        root = tree('|x| = 2')
        self.assertEqualPos(match_move_term(root),
                [P(root, split_absolute_equation)])

        root = tree('|x - 1| = 2')
        self.assertEqualPos(match_move_term(root),
                [P(root, split_absolute_equation)])

    def test_swap_sides(self):
        root, expect = tree('a = bx, bx = a')
        self.assertEqual(swap_sides(root, ()), expect)

    def test_subtract_term(self):
        root, a, expect = tree('x + a = b, a, x + a - a = b - a')
        self.assertEqual(subtract_term(root, (a,)), expect)

    def test_divide_term(self):
        root, a, expect = tree('x * a = b, a, (xa) / a = b / a')
        self.assertEqual(divide_term(root, (a,)), expect)

    def test_multiply_term(self):
        root, a, expect = tree('x / a = b, a, x / a * a = b * a')
        self.assertEqual(multiply_term(root, (a,)), expect)

    def test_split_absolute_equation(self):
        root, expect = tree('|x| = 2, x = 2 vv x = -2')
        self.assertEqual(split_absolute_equation(root, ()), expect)

        # FIXME: following call exeeds recursion limit
        # FIXME: self.assertValidate('|x - 1| = 2', 'x = -1 vv x = 3')

    def test_match_move_term_chain_negation(self):
        self.assertRewrite([
            '2x + 3 = -3x - 2',
            '2x + 3 - 3 = -3x - 2 - 3',
            '2x + 0 = -3x - 2 - 3',
            '2x = -3x - 2 - 3',
            '2x = -3x - 5',
            '2x - -3x = -3x - 5 - -3x',
            '2x + 3x = -3x - 5 - -3x',
            '(2 + 3)x = -3x - 5 - -3x',
            '5x = -3x - 5 - -3x',
            '5x = -3x - 5 + 3x',
            '5x = (-1 + 1)3x - 5',
            '5x = 0 * 3x - 5',
            '5x = 0 - 5',
            '5x = -5',
            '(5x) / 5 = (-5) / 5',
            '5 / 5 * x = (-5) / 5',
            '1x = (-5) / 5',
            'x = (-5) / 5',
            'x = -5 / 5',
            'x = -1',
        ])

    def test_match_move_term_chain_advanced(self):
        self.assertRewrite([
            '-x = a',
            '(-x)(-1) = a(-1)',
            '-x(-1) = a(-1)',
            '--x * 1 = a(-1)',
            '--x = a(-1)',
            'x = a(-1)',
            'x = -a * 1',
            'x = -a',
        ])

    def test_match_multiple_equations(self):
        eq0, eq1 = root = tree('x = 2 ^^ ay + x = 3')
        x = eq0[0]
        self.assertEqualPos(match_multiple_equations(root),
                [P(root, substitute_variable, (Scope(root), x, 2, eq1))])

        root = tree('x + y = 2 ^^ ay + x = 3')
        self.assertEqualPos(match_multiple_equations(root), [])

        root = tree('x + y ^^ ay + x = 3')
        self.assertEqualPos(match_multiple_equations(root), [])

    def test_substitute_variable(self):
        root, expect = tree('x = 2 ^^ ay + x = 3, x = 2 ^^ ay + 2 = 3')
        (x, l2), eq = root
        self.assertEqual(substitute_variable(root, ((Scope(root), x, l2, eq))),
                         expect)

    def test_match_double_case(self):
        a, b = root = tree('x = 2 vv x = 2')
        self.assertEqualPos(match_double_case(root),
                [P(root, double_case, (Scope(root), a, b))])

        root = tree('x = 2 vv x = -2')
        self.assertEqualPos(match_double_case(root), [])

    def test_double_case(self):
        a, b = root = tree('x = 2 vv x = 2, x = 2')
        self.assertEqual(double_case(root, (Scope(root), a, b)), a)
