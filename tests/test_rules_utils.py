from src.node import ExpressionNode as N
from src.rules.utils import nary_node, is_prime, least_common_multiple
from tests.test_rules_poly import tree
from tests.rulestestcase import RulesTestCase


class TestRulesUtils(RulesTestCase):

    def test_nary_node(self):
        a, b, c, d = tree('a,b,c,d')

        self.assertEqualNodes(nary_node('+', [a]), a)
        self.assertEqualNodes(nary_node('+', [a, b]), N('+', a, b))
        self.assertEqualNodes(nary_node('+', [a, b, c]),
                              N('+', N('+', a, b), c))
        self.assertEqualNodes(nary_node('+', [a, b, c, d]),
                              N('+', N('+', N('+', a, b), c), d))

    def test_is_prime(self):
        self.assertTrue(is_prime(2))
        self.assertTrue(is_prime(3))
        self.assertTrue(is_prime(647))

        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))
        self.assertFalse(is_prime(4))
        self.assertFalse(is_prime(9))
        self.assertFalse(is_prime(100))

    def test_least_common_multiple(self):
        self.assertEqual(least_common_multiple(5, 6), 30)
        self.assertEqual(least_common_multiple(5, 6, 15), 30)
        self.assertEqual(least_common_multiple(2, 4), 4)
