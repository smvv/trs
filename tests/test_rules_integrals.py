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
from src.rules.integrals import indef, choose_constant, solve_integral, \
        match_solve_indef, solve_indef, match_integrate_variable_power, \
        integrate_variable_root, integrate_variable_exponent, \
        match_constant_integral, constant_integral, single_variable_integral, \
        match_factor_out_constant, factor_out_integral_negation, \
        factor_out_constant, match_division_integral, division_integral, \
        extend_division_integral, match_function_integral, \
        logarithm_integral, sinus_integral, cosinus_integral, \
        match_sum_rule_integral, sum_rule_integral, \
        match_remove_indef_constant, remove_indef_constant
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesIntegrals(RulesTestCase):

    def test_choose_constant(self):
        a, b, c = tree('A, B, C')
        self.assertEqual(choose_constant(tree('int x ^ n')), c)
        self.assertEqual(choose_constant(tree('int x ^ c')), a)
        self.assertEqual(choose_constant(tree('int a ^ c da')), b)

    def test_match_solve_indef(self):
        root = tree('[x ^ 2]_a^b')
        self.assertEqualPos(match_solve_indef(root), [P(root, solve_indef)])

    def test_solve_integral(self):
        root, F, Fc = tree('int x ^ 2 dx, 1 / 3 x ^ 3, 1 / 3 x ^ 3 + C')
        self.assertEqual(solve_integral(root, F), Fc)
        x2, x, a, b = root = tree('int_a^b x ^ 2 dx')
        self.assertEqual(solve_integral(root, F), indef(Fc, a, b))

    def test_solve_integral_skip_indef(self):
        root, x, C, l1 = tree('int_a^b y ^ x dy, x, C, 1')
        F = tree('1 / (x + 1)y ^ (x + 1)')
        y, a, b = root[1:4]
        Fx = lambda y: l1 / (x + 1) * y ** (x + 1) + C
        self.assertEqual(solve_integral(root, F), Fx(b) - Fx(a))

    def test_solve_indef(self):
        root, expect = tree('[x ^ 2]_a^b, b ^ 2 - a ^ 2')
        self.assertEqual(solve_indef(root, ()), expect)

    def test_match_integrate_variable_power(self):
        root = tree('int x ^ n')
        self.assertEqualPos(match_integrate_variable_power(root),
                [P(root, integrate_variable_root)])

        root = tree('int x ^ n')
        self.assertEqualPos(match_integrate_variable_power(root),
                [P(root, integrate_variable_root)])

        root = tree('int -x ^ n')
        self.assertEqualPos(match_integrate_variable_power(root), [])

        for root in tree('int g ^ x, int g ^ x'):
            self.assertEqualPos(match_integrate_variable_power(root),
                    [P(root, integrate_variable_exponent)])

    def test_integrate_variable_root(self):
        root, expect = tree('int x ^ n, 1 / (n + 1) * x ^ (n + 1) + C')
        self.assertEqual(integrate_variable_root(root, ()), expect)

    def test_integrate_variable_exponent(self):
        root, expect = tree('int g ^ x, g ^ x / ln(g) + C')
        self.assertEqual(integrate_variable_exponent(root, ()), expect)

    def test_match_constant_integral(self):
        root = tree('int x dx')
        self.assertEqualPos(match_constant_integral(root),
                [P(root, single_variable_integral)])

        root = tree('int 2')
        self.assertEqualPos(match_constant_integral(root),
                [P(root, constant_integral)])

        root = tree('int c dx')
        self.assertEqualPos(match_constant_integral(root),
                [P(root, constant_integral)])

    def test_single_variable_integral(self):
        root, expect = tree('int x, int x ^ 1')
        self.assertEqual(single_variable_integral(root, ()), expect)

    def test_constant_integral(self):
        root, expect = tree('int 2, 2x + C')
        self.assertEqual(constant_integral(root, ()), expect)

        root, expect = tree('int_0^4 2, [2x + C]_0^4')
        self.assertEqual(constant_integral(root, ()), expect)

    def test_match_factor_out_constant(self):
        root, c, cx = tree('int cx dx, c, cx')
        self.assertEqualPos(match_factor_out_constant(root),
                [P(root, factor_out_constant, (Scope(cx), c))])

        root = tree('int -x2 dx')
        self.assertEqualPos(match_factor_out_constant(root),
                [P(root, factor_out_integral_negation)])

    def test_factor_out_integral_negation(self):
        root, expect = tree('int -x ^ 2 dx, -int x ^ 2 dx')
        self.assertEqual(factor_out_integral_negation(root, ()), expect)

    def test_factor_out_constant(self):
        root, expect = tree('int cx dx, c int x dx')
        c, x2 = cx2 = root[0]
        self.assertEqual(factor_out_constant(root, (Scope(cx2), c)), expect)

    def test_match_division_integral(self):
        root0, root1 = tree('int 1 / x, int 2 / x')
        self.assertEqualPos(match_division_integral(root0),
                [P(root0, division_integral)])
        self.assertEqualPos(match_division_integral(root1),
                [P(root1, extend_division_integral)])

    def test_division_integral(self):
        root, expect = tree('int 1 / x dx, ln|x| + C')
        self.assertEqual(division_integral(root, ()), expect)

    def test_extend_division_integral(self):
        root, expect = tree('int a / x dx, int a(1 / x) dx')
        self.assertEqual(extend_division_integral(root, ()), expect)

    def test_match_division_integral_chain(self):
        self.assertRewrite([
            'int a / x',
            'int a * 1 / x dx',
            'a(int 1 / x dx)',
            'a(ln(|x|) + C)',
            'a ln(|x|) + aC',
            # FIXME: 'a ln(|x|) + C',  # ac -> C
        ])

    def test_match_function_integral(self):
        root = tree('int ln x')
        self.assertEqualPos(match_function_integral(root),
                [P(root, logarithm_integral)])

        root = tree('int sin x')
        self.assertEqualPos(match_function_integral(root),
                [P(root, sinus_integral)])

        root = tree('int cos x')
        self.assertEqualPos(match_function_integral(root),
                [P(root, cosinus_integral)])

        root = tree('int sqrt x')
        self.assertEqualPos(match_function_integral(root), [])

    def test_logarithm_integral(self):
        root, expect = tree('int ln x, (xlnx - x) / ln e + C')
        self.assertEqual(logarithm_integral(root, ()), expect)

    def test_sinus_integral(self):
        root, expect = tree('int sin x, -cos x + C')
        self.assertEqual(sinus_integral(root, ()), expect)

    def test_cosinus_integral(self):
        root, expect = tree('int cos x, sin x + C')
        self.assertEqual(cosinus_integral(root, ()), expect)

    def test_match_sum_rule_integral(self):
        (f, g), x = root = tree('int (2x + 3x) dx')
        self.assertEqualPos(match_sum_rule_integral(root),
                [P(root, sum_rule_integral, (Scope(root[0]), f))])

        ((f, g), h), x = root = tree('int (2x + 3x + 4x) dx')
        self.assertEqualPos(match_sum_rule_integral(root),
                [P(root, sum_rule_integral, (Scope(root[0]), f)),
                 P(root, sum_rule_integral, (Scope(root[0]), g)),
                 P(root, sum_rule_integral, (Scope(root[0]), h))])

    def test_sum_rule_integral(self):
        ((f, g), h), x = root = tree('int (2x + 3x + 4x) dx')
        self.assertEqual(sum_rule_integral(root, (Scope(root[0]), f)),
                         tree('int 2x dx + int (3x + 4x) dx'))
        self.assertEqual(sum_rule_integral(root, (Scope(root[0]), g)),
                         tree('int 3x dx + int (2x + 4x) dx'))
        self.assertEqual(sum_rule_integral(root, (Scope(root[0]), h)),
                         tree('int 4x dx + int (2x + 3x) dx'))

    def test_match_remove_indef_constant(self):
        Fx, a, b = root = tree('[2x + C]_a^b')
        self.assertEqualPos(match_remove_indef_constant(root),
                [P(root, remove_indef_constant, (Scope(Fx), Fx[1]))])

        Fx, a, b = root = tree('[2x + x]_a^b')
        self.assertEqualPos(match_remove_indef_constant(root), [])

        Fx, a, b = root = tree('[2x]_a^b')
        self.assertEqualPos(match_remove_indef_constant(root), [])

    def test_remove_indef_constant(self):
        root, e = tree('[2x + C]_a^b, [2x]_a^b')
        Fx = root[0]
        self.assertEqual(remove_indef_constant(root, (Scope(Fx), Fx[1])), e)
