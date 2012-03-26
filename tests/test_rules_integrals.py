from src.rules.integrals import indef, choose_constant, solve_integral, \
        match_solve_indef, solve_indef, match_integrate_variable_power, \
        integrate_variable_root, integrate_variable_exponent
from src.rules.logarithmic import ln
#from .goniometry import sin, cos
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesIntegrals(RulesTestCase):

    def test_choose_constant(self):
        a, b, c = tree('a, b, c')
        self.assertEqual(choose_constant(tree('int x ^ n')), c)
        self.assertEqual(choose_constant(tree('int x ^ c')), a)
        self.assertEqual(choose_constant(tree('int a ^ c da')), b)

    def test_match_solve_indef(self):
        root = tree('[x ^ 2]_a^b')
        self.assertEqualPos(match_solve_indef(root), [P(root, solve_indef)])

    def test_solve_integral(self):
        root, F, Fc = tree('int x ^ 2 dx, 1 / 3 x ^ 3, 1 / 3 x ^ 3 + c')
        self.assertEqual(solve_integral(root, F), Fc)
        x2, x, a, b = root = tree('int_a^b x ^ 2 dx')
        self.assertEqual(solve_integral(root, F), indef(Fc, a, b))

    def test_solve_integral_skip_indef(self):
        root, x, c, l1 = tree('int_a^b y ^ x dy, x, c, 1')
        F = tree('1 / (x + 1)y ^ (x + 1)')
        y, a, b = root[1:4]
        Fx = lambda y: l1 / (x + 1) * y ** (x + 1) + c
        self.assertEqual(solve_integral(root, F), Fx(b) - Fx(a))

    def test_solve_indef(self):
        root, expect = tree('[x ^ 2]_a^b, b2 - a2')
        self.assertEqual(solve_indef(root, ()), expect)

    def test_match_integrate_variable_power(self):
        for root in tree('int x ^ n, int x ^ n'):
            self.assertEqualPos(match_integrate_variable_power(root),
                    [P(root, integrate_variable_root)])

        for root in tree('int g ^ x, int g ^ x'):
            self.assertEqualPos(match_integrate_variable_power(root),
                    [P(root, integrate_variable_exponent)])

    def test_integrate_variable_root(self):
        root, expect = tree('int x ^ n, x ^ (n + 1) / (n + 1) + c')
        self.assertEqual(integrate_variable_root(root, ()), expect)

    def test_integrate_variable_exponent(self):
        root, expect = tree('int g ^ x, g ^ x / ln(g) + c')
        self.assertEqual(integrate_variable_exponent(root, ()), expect)
