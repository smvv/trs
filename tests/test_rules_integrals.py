from src.rules.integrals import choose_constant, \
        match_integrate_variable_power, integrate_variable_root, \
        integrate_variable_exponent
from src.rules.logarithmic import ln
#from .goniometry import sin, cos
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesIntegrals(RulesTestCase):

    #def test_integral_params(self):
    #    f, x = root = tree('int fx dx')
    #    self.assertEqual(integral_params(root), (f, x))

    #    root = tree('int fx')
    #    self.assertEqual(integral_params(root), (f, x))

    #    root = tree('int 3')
    #    self.assertEqual(integral_params(root), (3, x))

    def test_choose_constant(self):
        a, b, c = tree('a, b, c')
        self.assertEqual(choose_constant(tree('int x ^ n')), c)
        self.assertEqual(choose_constant(tree('int x ^ c')), a)
        self.assertEqual(choose_constant(tree('int a ^ c da')), b)

    def test_match_integrate_variable_power(self):
        for root in tree('int x ^ n, int x ^ n'):
            self.assertEqualPos(match_integrate_variable_power(root),
                    [P(root, integrate_variable_root)])

        for root in tree('int g ^ x, int g ^ x'):
            self.assertEqualPos(match_integrate_variable_power(root),
                    [P(root, integrate_variable_exponent)])

    def test_integrate_variable_root(self):
        ((x, n), x), c = root, c = tree('int x ^ n, c')
        self.assertEqual(integrate_variable_root(root, ()),
                         x ** (n + 1) / (n + 1) + c)

    def test_integrate_variable_exponent(self):
        ((g, x), x), c = root, c = tree('int g ^ x, c')
        self.assertEqual(integrate_variable_exponent(root, ()),
                         g ** x / ln(g) + c)
