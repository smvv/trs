import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L
from src.rules.poly import match_combine_polynomes, combine_polynomes
from src.possibilities import Possibility as P
from src.parser import Parser
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


class TestRulesPoly(unittest.TestCase):

    #def test_match_combine_polynomes_numeric_combinations(self):
    #    l0, l1, l2 = L(1), L(2), L(2)
    #    plus = N('+', N('+', l0, l1), l2)
    #    p = match_combine_polynomes(plus)
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

    def test_numbers(self):
        l1, l2 = root = tree('1+2')
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((l1, (l1, l1, l1)),
                                             (l2, (l1, l2, l1))))])

    def test_identifiers_basic(self):
        l1, l2 = tree('1,2')
        a1, a2 = root = tree('a+a')
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((a1, (l1, a1, l1)),
                                             (a2, (l1, a2, l1))))])

    def test_identifiers_normal(self):
        l1, l2 = tree('1,2')
        a1, a2 = root = tree('a+2a')
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((a1, (l1, a1, l1)),
                                             (a2, (l2, a2[1], l1))))])

    def test_identifiers_reverse(self):
        l1, l2, la = tree('1,2,a')
        a1, a2 = root = tree('a+a*2')
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((a1, (l1, a1, l1)),
                                             (a2, (l2, la, l1))))])

    def test_identifiers_exponent(self):
        l1, l2 = tree('1,2')
        a1, a2 = root = tree('a2+a2')
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((a1, (l1, a1[0], l2)),
                                             (a2, (l1, a2[0], l2))))])


    def test_basic_subexpressions(self):
        a_b, c, d, l1, l5, l7 = tree('a+b,c,d,1,5,7')
        left, right = root = tree('(a+b)^d + (a+b)^d')

        self.assertEqual(left, right)
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((left, (l1, a_b, d)),
                                             (right, (l1, a_b, d))))])

        left, right = root = tree('5(a+b)^d + 7(a+b)^d')

        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((left, (l5, a_b, d)),
                                             (right, (l7, a_b, d))))])

        left, right = root = tree('c(a+b)^d + c(a+b)^d')

        self.assertEqual(left, right)
        self.assertEqualPos(match_combine_polynomes(root),
                [P(root, combine_polynomes, ((left, (c, a_b, d)),
                                             (right, (c, a_b, d))))])
