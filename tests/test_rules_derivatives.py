from src.rules.derivatives import der, get_derivation_variable, \
        match_zero_derivative, match_one_derivative, one_derivative, \
        zero_derivative, match_variable_power, variable_root, \
        variable_exponent, match_const_deriv_multiplication, \
        const_deriv_multiplication, chain_rule
from src.rules.logarithmic import ln
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesDerivatives(RulesTestCase):

    def test_get_derivation_variable(self):
        xy, x, l1 = tree('der(xy, x), der(x), der(1)')
        self.assertEqual(get_derivation_variable(xy), 'x')
        self.assertEqual(get_derivation_variable(x), 'x')
        self.assertIsNone(get_derivation_variable(l1))

        self.assertRaises(ValueError, tree, 'der(xy)')

    def test_match_zero_derivative(self):
        root = tree('der(x, y)')
        self.assertEqualPos(match_zero_derivative(root),
                [P(root, zero_derivative)])

        root = tree('der(2)')
        self.assertEqualPos(match_zero_derivative(root),
                [P(root, zero_derivative)])

    def test_zero_derivative(self):
        root = tree('der(1)')
        self.assertEqual(zero_derivative(root, ()), 0)

    def test_match_one_derivative(self):
        root = tree('der(x)')
        self.assertEqualPos(match_one_derivative(root),
                [P(root, one_derivative)])

        root = tree('der(x, x)')
        self.assertEqualPos(match_one_derivative(root),
                [P(root, one_derivative)])

    def test_one_derivative(self):
        root = tree('der(x)')
        self.assertEqual(one_derivative(root, ()), 1)

    def test_match_const_deriv_multiplication(self):
        root = tree('der(2x)')
        l2, x = root[0]
        self.assertEqualPos(match_const_deriv_multiplication(root),
                [P(root, const_deriv_multiplication, (Scope(root[0]), l2))])

    def test_match_const_deriv_multiplication_multiple_constants(self):
        root = tree('der(2x * 3)')
        (l2, x), l3 = root[0]
        scope = Scope(root[0])
        self.assertEqualPos(match_const_deriv_multiplication(root),
                [P(root, const_deriv_multiplication, (scope, l2)),
                 P(root, const_deriv_multiplication, (scope, l3))])

    def test_const_deriv_multiplication(self):
        root = tree('der(2x)')
        l2, x = root[0]
        args = Scope(root[0]), l2
        self.assertEqual(const_deriv_multiplication(root, args),
                         l2 * der(x, x))

    def test_match_variable_power(self):
        root, x, l2 = tree('der(x ^ 2), x, 2')
        self.assertEqualPos(match_variable_power(root),
                [P(root, variable_root)])

        root = tree('der(2 ^ x)')
        self.assertEqualPos(match_variable_power(root),
                [P(root, variable_exponent)])

    def test_match_variable_power_chain_rule(self):
        root, x, l2, x3 = tree('der((x ^ 3) ^ 2), x, 2, x ^ 3')
        self.assertEqualPos(match_variable_power(root),
                [P(root, chain_rule, (x3, variable_root, ()))])

        root = tree('der(2 ^ x ^ 3)')
        self.assertEqualPos(match_variable_power(root),
                [P(root, chain_rule, (x3, variable_exponent, ()))])

        # Below is not mathematically underivable, it's just not within the
        # scope of our program
        root, x = tree('der(x ^ x), x')
        self.assertEqualPos(match_variable_power(root), [])

    def test_variable_root(self):
        root = tree('der(x ^ 2)')
        x, n = root[0]
        self.assertEqual(variable_root(root, ()), n * x ** (n - 1))

    def test_variable_root_chain_rule(self):
        pass

    def test_chain_rule(self):
        pass
