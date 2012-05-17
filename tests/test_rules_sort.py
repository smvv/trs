from src.rules.sort import match_sort_polynome, swap_factors, get_poly_prop, \
        match_sort_monomial, iter_pairs, swap_mono, swap_poly, get_power_prop
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesSort(RulesTestCase):

    def test_swap_mono(self):
        self.assertTrue(swap_mono(tree('x, 1 / 2')))
        self.assertFalse(swap_mono(tree('2, 1 / 2')))

        self.assertTrue(swap_mono(tree('x, 2')))
        self.assertFalse(swap_mono(tree('2, x')))
        self.assertTrue(swap_mono(tree('x ^ 2, 2')))

        self.assertTrue(swap_mono(tree('y, x')))
        self.assertFalse(swap_mono(tree('x, y')))
        self.assertFalse(swap_mono(tree('x, x')))

        self.assertTrue(swap_mono(tree('x ^ 3, x ^ 2')))
        self.assertFalse(swap_mono(tree('x ^ 2, x ^ 3')))

    def test_swap_poly(self):
        self.assertTrue(swap_poly(tree('2, x')))
        self.assertFalse(swap_poly(tree('x, 2')))

        self.assertTrue(swap_poly(tree('a, a^2')))
        self.assertFalse(swap_poly(tree('a^2, a')))

        self.assertTrue(swap_poly(tree('y, x')))
        self.assertFalse(swap_poly(tree('x, y')))
        self.assertFalse(swap_poly(tree('x, x')))

        self.assertFalse(swap_poly(tree('x ^ 3, x ^ 2')))
        self.assertTrue(swap_poly(tree('x ^ 2, x ^ 3')))

    def test_get_power_prop(self):
        self.assertEqual(get_power_prop(tree('a')), ('a', 1))
        self.assertEqual(get_power_prop(tree('a ^ b')), ('a', 1))
        self.assertEqual(get_power_prop(tree('a ^ 2')), ('a', 2))
        self.assertEqual(get_power_prop(tree('a ^ -2')), ('a', -2))
        self.assertIsNone(get_power_prop(tree('1')))

    def test_get_poly_prop(self):
        self.assertEqual(get_poly_prop(tree('a ^ 2')), ('a', 2))
        self.assertEqual(get_poly_prop(tree('2a ^ 2')), ('a', 2))
        self.assertEqual(get_poly_prop(tree('ca ^ 2 * 2')), ('a', 2))
        self.assertEqual(get_poly_prop(tree('ab ^ 2')), ('a', 1))
        self.assertEqual(get_poly_prop(tree('a^3 * a^2')), ('a', 3))
        self.assertEqual(get_poly_prop(tree('a^2 * a^3')), ('a', 3))
        self.assertIsNone(get_poly_prop(tree('1')))

    def test_match_sort_monomial_constant(self):
        x, l2 = root = tree('x * 2')
        self.assertEqualPos(match_sort_monomial(root),
                [P(root, swap_factors, (Scope(root), x, l2))])

        root = tree('2x')
        self.assertEqualPos(match_sort_monomial(root), [])

    def test_match_sort_monomial_variables(self):
        y, x = root = tree('yx')
        self.assertEqualPos(match_sort_monomial(root),
                [P(root, swap_factors, (Scope(root), y, x))])

        root = tree('xy')
        self.assertEqualPos(match_sort_monomial(root), [])

    def test_match_sort_polynome(self):
        x, x2 = root = tree('x + x ^ 2')
        self.assertEqualPos(match_sort_polynome(root),
                [P(root, swap_factors, (Scope(root), x, x2))])

        root = tree('x + 2')
        self.assertEqualPos(match_sort_polynome(root), [])

    def test_swap_factors(self):
        x, l2 = root = tree('x * 2')
        self.assertEqualNodes(swap_factors(root, (Scope(root), x, l2)),
                              l2 * x)
