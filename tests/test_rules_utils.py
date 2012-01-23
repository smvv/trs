import unittest

from src.rules.utils import least_common_multiple


class TestRulesUtils(unittest.TestCase):

    def test_least_common_multiple(self):
        self.assertEqual(least_common_multiple(5, 6), 30)
        self.assertEqual(least_common_multiple(5, 6, 15), 30)
        self.assertEqual(least_common_multiple(2, 4), 4)
