from src.rules.poly import match_combine_polynomes, combine_polynomes
from src.rules.numerics import add_numerics
from src.possibilities import Possibility as P
from src.node import ExpressionLeaf as L
from src.parser import Parser
from tests.parser import ParserWrapper
from tests.rulestestcase import RulesTestCase


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


class TestRulesPoly(RulesTestCase):

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

    def test_match_add_numerics(self):
        l0, l1, l2 = tree('0,1,2')
        root = l0 + l1 + l2

        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (l0, l1, l0, l1)),
                 P(root, add_numerics, (l0, l2, l0, l2)),
                 P(root, add_numerics, (l1, l2, l1, l2))])

    def test_match_add_numerics_explicit_powers(self):
        l0, l1, l2 = tree('0^1,1*1,1*2^1')
        root = l0 + l1 + l2

        possibilities = match_combine_polynomes(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (l0, l1, l0[0], l1[1])),
                 P(root, add_numerics, (l0, l2, l0[0], l2[1][0])),
                 P(root, add_numerics, (l1, l2, l1[1], l2[1][0]))])

    def test_combine_polynomes(self):
        # 2a + 3a -> (2 + 3) * a
        l0, a, l1, l2 = tree('2,a,3,1')
        root = l0 * a + l1 * a
        left, right = root
        replacement = combine_polynomes(root, (left, right, l0, l1, a, 1))
        self.assertEqualNodes(replacement, (l0 + l1) * a)

        # a + 3a -> (1 + 3) * a
        root = a + l1 * a
        left, right = root
        replacement = combine_polynomes(root, (left, right, l2, l1, a, 1))
        self.assertEqualNodes(replacement, (l2 + l1) * a)

        # 2a + a -> (2 + 1) * a
        root = l0 * a + a
        left, right = root
        replacement = combine_polynomes(root, (left, right, l0, l2, a, 1))
        self.assertEqualNodes(replacement, (l0 + 1) * a)

        # a + a -> (1 + 1) * a
        root = a + a
        left, right = root
        replacement = combine_polynomes(root, (left, right, l2, l2, a, 1))
        self.assertEqualNodes(replacement, (l2 + 1) * a)
