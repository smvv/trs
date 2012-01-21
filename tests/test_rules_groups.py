from src.rules.groups import match_combine_groups, combine_groups
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesGroups(RulesTestCase):

    def test_match_combine_groups_no_const(self):
        a0, a1 = root = tree('a + a')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (1, a0, a0, 1, a1, a1))])

    def test_match_combine_groups_single_const(self):
        a0, mul = root = tree('a + 2a')
        l2, a1 = mul

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (1, a0, a0, l2, a1, mul))])

    def test_match_combine_groups_two_const(self):
        ((l2, a0), b), (l3, a1) = (m0, b), m1 = root = tree('2a + b + 3a')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (l2, a0, m0, l3, a1, m1))])

    def test_match_combine_groups_n_const(self):
        ((l2, a0), (l3, a1)), (l4, a2) = (m0, m1), m2 = root = tree('2a+3a+4a')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (l2, a0, m0, l3, a1, m1)),
                 P(root, combine_groups, (l2, a0, m0, l4, a2, m2)),
                 P(root, combine_groups, (l3, a1, m1, l4, a2, m2))])

    def test_match_combine_groups_identifier_group_no_const(self):
        ab0, ab1 = root = tree('ab + ab')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (1, ab0, ab0, 1, ab1, ab1))])

    def test_match_combine_groups_identifier_group_single_const(self):
        m0, m1 = root = tree('ab + 2ab')
        (l2, a), b = m1

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (1, m0, m0, l2, a * b, m1))])

    def test_match_combine_groups_identifier_group_unordered(self):
        m0, m1 = root = tree('ab + ba')
        b, a = m1

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (1, m0, m0, 1, b * a, m1))])

    def test_combine_groups_simple(self):
        root, l1 = tree('a + a,1')
        a0, a1 = root

        self.assertEqualNodes(combine_groups(root, (1, a0, a0, 1, a1, a1)),
                              (l1 + 1) * a0)

    def test_combine_groups_nary(self):
        root, l1 = tree('ab + b + ba,1')
        abb, ba = root
        ab, b = abb

        self.assertEqualNodes(combine_groups(root, (1, ab, ab, 1, ba, ba)),
                              (l1 + 1) * ab + b)
