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

            for pair in zip(p.args, e.args):
                self.assertEqual(*pair)

            self.assertEqual(p, e)

    def test_basic(self):
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

        a1, a2 = root = tree('a+a*2')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((a1, (a1, l1, l1, False)),
                                             (a2, (a2[1], l1, l2, False))))])

        a1, a2 = root = tree('a2+a2')
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((a1, (a1[0], l2, l1, True)),
                                             (a2, (a2[0], l2, l1, True))))])


    def test_basic_subexpressions(self):
        return # TODO: test this!!
        a_b = tree('a+b')
        c, d = tree('c+d')
        l1 = tree('1')
        l5, l7 = tree('5+7')

        left, right = root = tree('(a+b)^d + (a+b)^d')

        self.assertEqual(left, right)
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((left, (a_b, d, l1, True)),
                                             (right, (a_b, d, l1, True))))])

        left, right = root = tree('5(a+b)^d + 7(a+b)^d')

        #<Possibility root="5 * (a + b) ^ d + 7 * (a + b) ^ d"
        #    handler=combine_polynomes args=((<src.node.ExpressionNode object at
        #    0x9fb2e0c>, (<src.node.ExpressionNode object at 0x9fb2c2c>,
        #    'd', 5, True)), (<src.node.ExpressionNode object at
        #    0x9fb438c>, (<src.node.ExpressionNode object at
        #    0x9fb2f0c>, 'd', 7, True)))>

        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((left, (a_b, d, l5, True)),
                                             (right, (a_b, d, l7, True))))])

        left, right = root = tree('c(a+b)^d + c(a+b)^d')

        self.assertEqual(left, right)
        self.assertEqualPos(match_combine_factors(root),
                [P(root, combine_polynomes, ((left, (left[0], c, d, True)),
                                             (right, (right[0], c, d, True))))])
