import unittest

from src.rules.poly import match_combine_polynomes, combine_polynomes, \
        combine_numerics
from src.possibilities import Possibility as P
from src.parser import Parser
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


class TestRulesPoly(unittest.TestCase):

    def assertEqualPos(self, possibilities, expected):
        self.assertEqual(len(possibilities), len(expected))

        for p, e in zip(possibilities, expected):
            self.assertEqual(p.root, e.root)

            for pair in zip(p.args, e.args):
                self.assertEqual(*pair)

            self.assertEqual(p, e)

    def test_numbers(self):
        return
        # TODO: Move to combine numeric test
        l1, l2 = root = tree('1+2')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_numerics, ((l1, (l1, l1, l1)),
                                             (l2, (l1, l2, l1))))])

    def test_identifiers_basic(self):
        a1, a2 = root = tree('a+a')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 1, 1, 'a', 1))])

    def test_identifiers_normal(self):
        a1, a2 = root = tree('a+2a')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 1, 2, 'a', 1))])

    def test_identifiers_reverse(self):
        return
        # TODO: Move to normalisation test
        a1, a2 = root = tree('a+a*2')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 1, 2, a1, 1))])

    def test_identifiers_exponent(self):
        a1, a2 = root = tree('a2+a2')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 1, 1, 'a', 2))])

    def test_identifiers_coeff_exponent_left(self):
        a1, a2 = root = tree('2a3+a3')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 2, 1, 'a', 3))])


    def test_identifiers_coeff_exponent_both(self):
        a1, a2 = root = tree('2a3+2a3')
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (a1, a2, 2, 2, 'a', 3))])


    def test_basic_subexpressions(self):
        a_b, c, d = tree('a+b,c,d')
        left, right = root = tree('(a+b)^d + (a+b)^d')

        self.assertEqual(left, right)
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (left, right, 1, 1, a_b, d))])

        left, right = root = tree('5(a+b)^d + 7(a+b)^d')

        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, (left, right, 5, 7, a_b, d))])

        # TODO: Move to other strategy
        #left, right = root = tree('c(a+b)^d + c(a+b)^d')

        #self.assertEqual(left, right)
        #possibilities = match_combine_polynomes(root)
        #self.assertEqualPos(possibilities,
        #        [P(root, combine_polynomes, (left, right, c, c, a_b, d))])

    def test_match_combine_polynomes_numeric_combinations(self):
        return
        root = tree('0+1+2')
        # TODO: this test fails with this code: l0, l1, l2 = tree('0,1,2')
        l0, l1, l2 = root[0][0], root[0][1], root[1]
        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_polynomes, ((l0, (l1, l0, l1)),
                                             (l1, (l1, l1, l1)))),
                 P(root, combine_polynomes, ((l0, (l1, l0, l1)),
                                             (l2, (l1, l2, l1)))),
                 P(root, combine_polynomes, ((l1, (l1, l1, l1)),
                                             (l2, (l1, l2, l1))))])
