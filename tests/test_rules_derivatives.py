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
from src.rules.derivatives import get_derivation_variable, \
        match_zero_derivative, match_one_derivative, one_derivative, \
        zero_derivative, match_variable_power, variable_root, \
        variable_exponent, match_const_deriv_multiplication, \
        const_deriv_multiplication, chain_rule, match_logarithmic, \
        logarithmic, match_goniometric, sinus, cosinus, tangens, \
        match_sum_product_rule, sum_rule, product_rule, match_quotient_rule, \
        quotient_rule, power_rule
from src.node import Scope, sin, cos, ln, der
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesDerivatives(RulesTestCase):

    def test_get_derivation_variable(self):
        xy0, xy1, x, l1 = tree('d/dx xy, (xy)\', x\', 1\'')
        self.assertEqual(get_derivation_variable(xy0), 'x')
        self.assertEqual(get_derivation_variable(xy1), 'x')
        self.assertEqual(get_derivation_variable(x), 'x')
        self.assertIsNone(get_derivation_variable(l1))

    def test_match_zero_derivative(self):
        root = tree('d/dy x')
        self.assertEqualPos(match_zero_derivative(root),
                [P(root, zero_derivative)])

        root = tree('d/dx 2')
        self.assertEqualPos(match_zero_derivative(root),
                [P(root, zero_derivative)])

    def test_zero_derivative(self):
        root = tree('d/dx 1')
        self.assertEqual(zero_derivative(root, ()), 0)

    def test_match_one_derivative(self):
        root = tree('d/dx x')
        self.assertEqualPos(match_one_derivative(root),
                [P(root, one_derivative)])

        root = tree('d/dx x')
        self.assertEqualPos(match_one_derivative(root),
                [P(root, one_derivative)])

    def test_one_derivative(self):
        root = tree('d/dx x')
        self.assertEqual(one_derivative(root, ()), 1)

    def test_match_const_deriv_multiplication(self):
        root = tree('d/dx 2x')
        l2, x = root[0]
        self.assertEqualPos(match_const_deriv_multiplication(root),
                [P(root, const_deriv_multiplication, (Scope(root[0]), l2, x))])

        (x, y), x = root = tree('d/dx xy')
        self.assertEqualPos(match_const_deriv_multiplication(root),
                [P(root, const_deriv_multiplication, (Scope(root[0]), y, x))])

    def test_match_const_deriv_multiplication_multiple_constants(self):
        root = tree('d/dx 2x * 3')
        (l2, x), l3 = root[0]
        scope = Scope(root[0])
        self.assertEqualPos(match_const_deriv_multiplication(root),
                [P(root, const_deriv_multiplication, (scope, l2, x)),
                 P(root, const_deriv_multiplication, (scope, l3, x))])

    def test_const_deriv_multiplication(self):
        root = tree('d/dx 2x')
        l2, x = root[0]
        args = Scope(root[0]), l2, x
        self.assertEqual(const_deriv_multiplication(root, args),
                         l2 * der(x, x))

    def test_match_variable_power(self):
        root, x, l2 = tree('d/dx x ^ 2, x, 2')
        self.assertEqualPos(match_variable_power(root),
                [P(root, variable_root)])

        root = tree('d/dx 2 ^ x')
        self.assertEqualPos(match_variable_power(root),
                [P(root, variable_exponent)])

    def test_match_variable_power_chain_rule(self):
        root, x, l2, x3 = tree('d/dx (x ^ 3) ^ 2, x, 2, x ^ 3')
        self.assertEqualPos(match_variable_power(root),
                [P(root, chain_rule, (x3, variable_root, ()))])

        root = tree('d/dx 2 ^ x ^ 3')
        self.assertEqualPos(match_variable_power(root),
                [P(root, chain_rule, (x3, variable_exponent, ()))])

        # Below is not mathematically underivable, it's just not within the
        # scope of our program
        root, x = tree('d/dx x ^ x, x')
        self.assertEqualPos(match_variable_power(root),
                [P(root, power_rule)])

    def test_power_rule(self):
        root, expect = tree("[x ^ x]', [e ^ ln(x ^ x)]'")
        self.assertEqual(power_rule(root, ()), expect)

    def test_power_rule_chain(self):
        self.assertRewrite([
            "[x ^ x]'",
            "[e ^ (ln x ^ x)]'",
            "e ^ (ln x ^ x)[ln x ^ x]'",
            "x ^ x * [ln x ^ x]'",
            "x ^ x * [x ln x]'",
            "x ^ x * ([x]' * ln x + x[ln x]')",
            "x ^ x * (1ln x + x[ln x]')",
            "x ^ x * (ln x + x[ln x]')",
            "x ^ x * (ln x + x * 1 / x)",
            "x ^ x * (ln x + (x * 1) / x)",
            "x ^ x * (ln x + x / x)",
            "x ^ x * (ln x + 1)",
            "x ^ x * ln x + x ^ x * 1",
            "x ^ x * ln x + x ^ x",
        ])

    def test_variable_root(self):
        root = tree('d/dx x ^ 2')
        x, n = root[0]
        self.assertEqual(variable_root(root, ()), n * x ** (n - 1))

    def test_variable_exponent(self):
        root = tree('d/dx 2 ^ x')
        g, x = root[0]
        self.assertEqual(variable_exponent(root, ()), g ** x * ln(g))

        root = tree('d/dx e ^ x')
        e, x = root[0]
        self.assertEqual(variable_exponent(root, ()), e ** x)

    def test_chain_rule(self):
        root = tree('(2 ^ x ^ 3)\'')
        l2, x3 = root[0]
        x, l3 = x3
        self.assertEqual(chain_rule(root, (x3, variable_exponent, ())),
                          l2 ** x3 * ln(l2) * der(x3))

    def test_match_logarithmic(self):
        root = tree('d/dx log(x)')
        self.assertEqualPos(match_logarithmic(root), [P(root, logarithmic)])

    def test_match_logarithmic_chain_rule(self):
        root, f = tree('d/dx log(x ^ 2), x ^ 2')
        self.assertEqualPos(match_logarithmic(root),
                [P(root, chain_rule, (f, logarithmic, ()))])

    def test_logarithmic(self):
        root, x, l1, l10 = tree('d/dx log(x), x, 1, 10')
        self.assertEqual(logarithmic(root, ()), l1 / (x * ln(l10)))

        root, x, l1, l10 = tree('d/dx ln(x), x, 1, 10')
        self.assertEqual(logarithmic(root, ()), l1 / x)

    def test_match_goniometric(self):
        root = tree('d/dx sin(x)')
        self.assertEqualPos(match_goniometric(root), [P(root, sinus)])

        root = tree('d/dx cos(x)')
        self.assertEqualPos(match_goniometric(root), [P(root, cosinus)])

        root = tree('d/dx tan(x)')
        self.assertEqualPos(match_goniometric(root), [P(root, tangens)])

    def test_match_goniometric_chain_rule(self):
        root, x2 = tree('d/dx sin(x ^ 2), x ^ 2')
        self.assertEqualPos(match_goniometric(root),
                [P(root, chain_rule, (x2, sinus, ()))])

        root = tree('d/dx cos(x ^ 2)')
        self.assertEqualPos(match_goniometric(root),
                [P(root, chain_rule, (x2, cosinus, ()))])

    def test_sinus(self):
        root, x = tree('d/dx sin(x), x')
        self.assertEqual(sinus(root, ()), cos(x))

    def test_cosinus(self):
        root, x = tree('d/dx cos(x), x')
        self.assertEqual(cosinus(root, ()), -sin(x))

    def test_tangens(self):
        root, x = tree('d/dx tan(x), x')
        self.assertEqual(tangens(root, ()), der(sin(x) / cos(x), x))

        root = tree('tan(x)\'')
        self.assertEqual(tangens(root, ()), der(sin(x) / cos(x)))

    def test_match_sum_product_rule_sum(self):
        root = tree('d/dx (x ^ 2 + x)')
        x2, x = f = root[0]
        self.assertEqualPos(match_sum_product_rule(root),
                [P(root, sum_rule, (Scope(f), x2)),
                 P(root, sum_rule, (Scope(f), x))])

        root = tree('d/dx (x ^ 2 + 3 + x)')
        self.assertEqualPos(match_sum_product_rule(root),
                [P(root, sum_rule, (Scope(root[0]), x2)),
                 P(root, sum_rule, (Scope(root[0]), x))])

    def test_match_sum_product_rule_product(self):
        root = tree('d/dx x ^ 2 * x')
        x2, x = f = root[0]
        self.assertEqualPos(match_sum_product_rule(root),
                [P(root, product_rule, (Scope(f), x2)),
                 P(root, product_rule, (Scope(f), x))])

    def test_match_sum_product_rule_none(self):
        root = tree('d/dx (2 + 2)')
        self.assertEqualPos(match_sum_product_rule(root), [])

        root = tree('d/dx x ^ 2 * 2')
        self.assertEqualPos(match_sum_product_rule(root), [])

    def test_sum_rule(self):
        root = tree('(x ^ 2 + x)\'')
        x2, x = f = root[0]
        self.assertEqual(sum_rule(root, (Scope(f), x2)), der(x2) + der(x))
        self.assertEqual(sum_rule(root, (Scope(f), x)), der(x) + der(x2))

        root = tree('(x ^ 2 + 3 + x)\'')
        (x2, l3), x = f = root[0]
        self.assertEqual(sum_rule(root, (Scope(f), x2)), der(x2) + der(l3 + x))
        self.assertEqual(sum_rule(root, (Scope(f), x)), der(x) + der(x2 + l3))

    def test_product_rule(self):
        root = tree('(x ^ 2 * x)\'')
        x2, x = f = root[0]
        self.assertEqual(product_rule(root, (Scope(f), x2)),
                         der(x2) * x + x2 * der(x))
        self.assertEqual(product_rule(root, (Scope(f), x)),
                         der(x) * x2 + x * der(x2))

        root = tree('(x ^ 2 * x * x ^ 3)\'')
        (x2, x), x3 = f = root[0]
        self.assertEqual(product_rule(root, (Scope(f), x2)),
                         der(x2) * (x * x3) + x2 * der(x * x3))
        self.assertEqual(product_rule(root, (Scope(f), x)),
                         der(x) * (x2 * x3) + x * der(x2 * x3))
        self.assertEqual(product_rule(root, (Scope(f), x3)),
                         der(x3) * (x2 * x) + x3 * der(x2 * x))

    def test_match_quotient_rule(self):
        root = tree('d/dx x ^ 2 / x')
        self.assertEqualPos(match_quotient_rule(root),
                [P(root, quotient_rule)])

        root = tree('d/dx x ^ 2 / 2')
        self.assertEqualPos(match_quotient_rule(root), [])

    def test_quotient_rule(self):
        root = tree('(x ^ 2 / x)\'')
        f, g = root[0]
        self.assertEqual(quotient_rule(root, ()),
                         (der(f) * g - f * der(g)) / g ** 2)

    #def test_natural_pase_chain(self):
    #    self.assertRewrite([
    #        'der(e ^ x)',
    #        'e ^ x * ln(e)',
    #        'e ^ x * 1',
    #        'e ^ x',
    #    ])
