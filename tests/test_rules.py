import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L
from src.rules.poly import match_combine_factors, combine_numerics, \
        combine_orders
from src.rules.utils import nary_node
from src.possibilities import Possibility as P


class TestRules(unittest.TestCase):

    def test_nary_node_binary(self):
        l0, l1 = L(1), L(2)
        plus = N('+', l0, l1)
        self.assertEqual(nary_node('+', [l0, l1]), plus)

    def test_nary_node_ternary(self):
        l0, l1, l2 = L(1), L(2), L(3)
        plus = N('+', N('+', l0, l1), l2)
        self.assertEqual(nary_node('+', [l0, l1, l2]), plus)

    def test_match_combine_factors_numeric_simple(self):
        l0, l1 = L(1), L(2)
        plus = N('+', l0, l1)
        p = match_combine_factors(plus)
        self.assertEqualPos(p, [P(plus, combine_numerics, (l0, l1))])

    def test_match_combine_factors_numeric_combinations(self):
        l0, l1, l2 = L(1), L(2), L(2)
        plus = N('+', N('+', l0, l1), l2)
        p = match_combine_factors(plus)
        self.assertEqualPos(p, [P(plus, combine_numerics, (l0, l1)),
                                P(plus, combine_numerics, (l0, l2)),
                                P(plus, combine_numerics, (l1, l2))])

    def assertEqualPos(self, possibilities, expected):
        for p, e in zip(possibilities, expected):
            self.assertEqual(p.root, e.root)
            self.assertEqual(p.handler, e.handler)
            self.assertEqual(p.args, e.args)
