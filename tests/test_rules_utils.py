import unittest

from src.rules.utils import least_common_multiple, is_fraction
from tests.rulestestcase import tree


class TestRulesUtils(unittest.TestCase):

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
