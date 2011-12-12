import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L
from src.rules.poly import match_combine_factors, combine_polynomes
from src.possibilities import Possibility as P
from src.parser import Parser
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


class TestRulesPoly(unittest.TestCase):

    #def test_match_combine_factors_numeric_combinations(self):
    #    l0, l1, l2 = L(1), L(2), L(2)
    #    plus = N('+', N('+', l0, l1), l2)
    #    p = match_combine_factors(plus)
    #    self.assertEqualPos(p, [P(plus, combine_polynomes, (l0, l1)),
    #                            P(plus, combine_polynomes, (l0, l2)),
    #                            P(plus, combine_polynomes, (l1, l2))])

    def assertEqualPos(self, possibilities, expected):
        self.assertEqual(len(possibilities), len(expected))

        for p, e in zip(possibilities, expected):
            self.assertEqual(p.root, e.root)
            self.assertEqual(p, e)

    def test_numeric(self):
        l1, l2 = root = tree('1+2')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((l1, (l1, l1, l1, False)),
                                             (l2, (l2, l1, l1, False))))])

        a1, a2 = root = tree('a+a')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((a1, (a1, l1, l1, False)),
                                             (a2, (a2, l1, l1, False))))])

        a1, a2 = root = tree('a+2a')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((a1, (a1, l1, l1, False)),
                                             (a2, (a2[1], l1, l2, False))))])

        a1, a2 = root = tree('a2+a2')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((a1, (a1[0], l2, l1, True)),
                                             (a2, (a2[0], l2, l1, True))))])
