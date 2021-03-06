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
from src.rules import utils
from src.rules.utils import least_common_multiple, is_fraction, partition, \
        find_variables, first_sorted_variable, find_variable, substitute, \
        divides, dividers, is_prime, prime_dividers, evals_to_numeric, \
        iter_pairs, range_except
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

    def test_substitute(self):
        x, a = tree('x, a')

        self.assertEqual(substitute(x, x, a), a)
        self.assertEqual(substitute(tree('x2'), x, a), tree('a2'))
        self.assertEqual(substitute(tree('y + x + 1'), x, a),
                         tree('y + a + 1'))
        self.assertEqual(substitute(tree('1 - 2x'), x, a),
                         tree('1 - 2a'))

    def test_divides(self):
        self.assertTrue(divides(3, 3))
        self.assertTrue(divides(2, 4))
        self.assertTrue(divides(7, 21))
        self.assertFalse(divides(4, 2))
        self.assertFalse(divides(2, 3))

    def test_dividers(self):
        self.assertEqual(dividers(1), [])
        self.assertEqual(dividers(2), [])
        self.assertEqual(dividers(4), [2])
        self.assertEqual(dividers(6), [2, 3])
        self.assertEqual(dividers(10), [2, 5])
        self.assertEqual(dividers(21), [3, 7])
        self.assertEqual(dividers(20), [2, 4, 5, 10])
        self.assertEqual(dividers(1000000), [2, 4, 5, 8, 10, 16, 20, 25, 32,
            40, 50, 64, 80, 100, 125, 160, 200, 250, 320, 400, 500, 625, 800,
            1000, 1250, 1600, 2000, 2500, 3125, 4000, 5000, 6250, 8000, 10000,
            12500, 15625, 20000, 25000, 31250, 40000, 50000, 62500, 100000,
            125000, 200000, 250000, 500000])

    def test_is_prime(self):
        self.assertFalse(is_prime(1))
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertFalse(is_prime(6))
        self.assertFalse(is_prime(9))
        self.assertTrue(is_prime(19))
        self.assertTrue(is_prime(43))

    def test_prime_dividers(self):
        self.assertEqual(prime_dividers(6), [2, 3])
        self.assertEqual(prime_dividers(20), [2, 5])

    def test_evals_to_numeric(self):
        self.assertTrue(evals_to_numeric(tree('1')))
        self.assertFalse(evals_to_numeric(tree('a')))
        self.assertTrue(evals_to_numeric(tree('1 + 2')))
        self.assertFalse(evals_to_numeric(tree('1 + a')))
        self.assertTrue(evals_to_numeric(tree('1 + 2 / 2 * 9')))
        self.assertFalse(evals_to_numeric(tree('int 1')))
        self.assertFalse(evals_to_numeric(tree('int a')))
        self.assertTrue(evals_to_numeric(tree('sqrt 1')))

    def test_iter_pairs(self):
        self.assertEqual(list(iter_pairs([1])), [])
        self.assertEqual(list(iter_pairs([1, 2])), [(1, 2)])
        self.assertEqual(list(iter_pairs([1, 2, 3])), [(1, 2), (2, 3)])
        self.assertEqual(list(iter_pairs([1, 2, 3, 4])), [(1, 2), (2, 3), (3, 4)])

    def test_range_except(self):
        self.assertEqual(range_except(0, 5, 2), [0, 1, 3, 4])
        self.assertEqual(range_except(0, 4, 0), [1, 2, 3])
        self.assertEqual(range_except(0, 3, 3), [0, 1, 2])
