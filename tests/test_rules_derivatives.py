from src.rules.derivatives import get_derivation_variable, \
        match_constant_derivative, one_derivative, zero_derivative
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesDerivatives(RulesTestCase):

    def test_get_derivation_variable(self):
        xy, x, l1 = tree('der(xy, x), der(x), der(1)')
        self.assertEqual(get_derivation_variable(xy), 'x')
        self.assertEqual(get_derivation_variable(x), 'x')
        self.assertIsNone(get_derivation_variable(l1))

        self.assertRaises(ValueError, tree, 'der(xy)')

    def test_match_constant_derivative(self):
        root = tree('der(x)')
        self.assertEqualPos(match_constant_derivative(root),
                [P(root, one_derivative, ())])

        root = tree('der(x, x)')
        self.assertEqualPos(match_constant_derivative(root),
                [P(root, one_derivative, ())])

        root = tree('der(x, y)')
        self.assertEqualPos(match_constant_derivative(root),
                [P(root, zero_derivative, ())])

        root = tree('der(2)')
        self.assertEqualPos(match_constant_derivative(root),
                [P(root, zero_derivative, ())])

    def test_one_derivative(self):
        root = tree('der(x)')
        self.assertEqual(one_derivative(root, ()), 1)

    def test_zero_derivative(self):
        root = tree('der(1)')
        self.assertEqual(zero_derivative(root, ()), 0)
