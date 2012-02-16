
from src.rules.negation import match_negated_division, \
        single_negated_division, double_negated_division
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNegation(RulesTestCase):

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
                [P(root, double_negated_division, (root,))])

    def test_single_negated_division(self):
        l1, l2 = root = tree('-1 / 2')
        self.assertEqualNodes(single_negated_division(root, (+l1, l2)),
                              -(+l1 / l2))

        l1, l2 = root = tree('1 / -2')
        self.assertEqualNodes(single_negated_division(root, (l1, +l2)),
                              -(l1 / +l2))

    def test_double_negated_division(self):
        l1, l2 = root = tree('-1 / -2')

        self.assertEqualNodes(double_negated_division(root, (root,)),
                              +l1 / +l2)
