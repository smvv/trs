from src.rules.negation import match_negated_factor, negated_factor, \
        match_negate_polynome, negate_polynome, double_negation, \
        match_negated_division, single_negated_division, \
        double_negated_division
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNegation(RulesTestCase):

    def test_match_negated_factor(self):
        a, b = root = tree('a * -b')
        self.assertEqualPos(match_negated_factor(root),
                [P(root, negated_factor, (Scope(root), b))])

        (a, b), c = root = tree('a * -b * -c')
        scope = Scope(root)
        self.assertEqualPos(match_negated_factor(root),
                [P(root, negated_factor, (scope, b)),
                 P(root, negated_factor, (scope, c))])

    def test_negated_factor(self):
        a, b = root = tree('a * -b')
        self.assertEqualNodes(negated_factor(root, (Scope(root), b)),
                              -(a * +b))

        (a, b), c = root = tree('a * -b * -c')
        scope = Scope(root)
        self.assertEqualNodes(negated_factor(root, (scope, b)),
                              -(a * +b * c))
        self.assertEqualNodes(negated_factor(root, (scope, c)),
                              -(a * b * +c))

    def test_match_negate_polynome(self):
        root = tree('--a')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, double_negation, ())])

        root = tree('-(a + b)')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, negate_polynome, ())])

        a, b = root = tree('-(a - -b)')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, double_negation, (b,)),
                 P(root, negate_polynome, ())])

    def test_negate_polynome(self):
        a, b = root = tree('-(a + b)')
        self.assertEqualNodes(negate_polynome(root, ()), -a + -b)

        a, b = root = tree('-(a - b)')
        self.assertEqualNodes(negate_polynome(root, ()), -a + -b)

    def test_match_negated_division_none(self):
        self.assertEqual(match_negated_division(tree('1 / 2')), [])

    def test_match_negated_division_single(self):
        l1, l2 = root = tree('-1 / 2')
        possibilities = match_negated_division(root)
        self.assertEqualPos(possibilities,
                [P(root, single_negated_division, (+l1, l2))])

        l1, l2 = root = tree('1 / -2')
        possibilities = match_negated_division(root)
        self.assertEqualPos(possibilities,
                [P(root, single_negated_division, (l1, +l2))])

    def test_match_negated_division_double(self):
        root = tree('-1 / -2')

        possibilities = match_negated_division(root)
        self.assertEqualPos(possibilities,
                [P(root, double_negated_division, ())])

    def test_single_negated_division(self):
        l1, l2 = root = tree('-1 / 2')
        self.assertEqualNodes(single_negated_division(root, (+l1, l2)),
                              -(+l1 / l2))

        l1, l2 = root = tree('1 / -2')
        self.assertEqualNodes(single_negated_division(root, (l1, +l2)),
                              -(l1 / +l2))

    def test_double_negated_division(self):
        l1, l2 = root = tree('-1 / -2')

        self.assertEqualNodes(double_negated_division(root, ()),
                              +l1 / +l2)
