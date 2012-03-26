from src.rules import utils
from src.rules.utils import least_common_multiple, is_fraction, partition, \
        find_variables, first_sorted_variable, find_variable, \
        replace_variable, infinity
from tests.rulestestcase import tree, RulesTestCase


class TestRulesUtils(RulesTestCase):

    def test_doctest(self):
        self.assertDoctests(utils)

    def test_least_common_multiple(self):
        self.assertEqual(least_common_multiple(5, 6), 30)
        self.assertEqual(least_common_multiple(5, 6, 15), 30)
        self.assertEqual(least_common_multiple(2, 4), 4)

    def test_is_fraction(self):
        l1, a = tree('1, a')

        self.assertTrue(is_fraction(a / 2, a, 2))
        self.assertTrue(is_fraction(l1 / 2 * a, a, 2))
        self.assertTrue(is_fraction(a * (l1 / 2), a, 2))
        self.assertFalse(is_fraction(l1 / 3 * a, a, 2))
        self.assertFalse(is_fraction(l1, a, 2))

    def test_partition(self):
        self.assertEqual(partition(lambda x: x & 1, range(6)),
                         ([1, 3, 5], [0, 2, 4]))

    def test_infinity(self):
        self.assertEqual(infinity(), tree('oo'))

    def test_find_variables(self):
        x, l2, add, mul0, mul1 = tree('x, 2, x + 2, 2x, xy')
        self.assertSetEqual(find_variables(x), set(['x']))
        self.assertSetEqual(find_variables(l2), set())
        self.assertSetEqual(find_variables(add), set(['x']))
        self.assertSetEqual(find_variables(mul0), set(['x']))
        self.assertSetEqual(find_variables(mul1), set(['x', 'y']))

    def test_first_sorted_variable(self):
        self.assertEqual(first_sorted_variable(set('ax')), 'x')
        self.assertEqual(first_sorted_variable(set('ay')), 'y')
        self.assertEqual(first_sorted_variable(set('az')), 'z')
        self.assertEqual(first_sorted_variable(set('xz')), 'x')
        self.assertEqual(first_sorted_variable(set('bac')), 'a')

    def test_find_variable(self):
        x, y = tree('x, y')

        self.assertEqual(find_variable(tree('x')), x)
        self.assertEqual(find_variable(tree('x ^ 2')), x)
        self.assertEqual(find_variable(tree('1 + 2')), x)
        self.assertEqual(find_variable(tree('y ^ 2')), y)

    def test_replace_variable(self):
        x, a = tree('x, a')

        self.assertEqual(replace_variable(x, x, a), a)
        self.assertEqual(replace_variable(tree('x2'), x, a), tree('a2'))
        self.assertEqual(replace_variable(tree('y + x + 1'), x, a),
                         tree('y + a + 1'))
