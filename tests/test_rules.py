import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L
from src.rules.utils import nary_node


class TestRules(unittest.TestCase):

    def test_nary_node_binary(self):
        l0, l1 = L(1), L(2)
        plus = N('+', l0, l1)
        self.assertEqual(nary_node('+', [l0, l1]), plus)

    def test_nary_node_ternary(self):
        l0, l1, l2 = L(1), L(2), L(3)
        plus = N('+', N('+', l0, l1), l2)
        self.assertEqual(nary_node('+', [l0, l1, l2]), plus)
