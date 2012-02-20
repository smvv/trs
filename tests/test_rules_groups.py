from src.rules.groups import match_combine_groups, combine_groups
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesGroups(RulesTestCase):

    def test_match_combine_groups_no_const(self):
        root, l1 = tree('a + a,1')
        a0, a1 = root

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l1, a0, a0,
                                                       l1, a1, a1))])

    def test_match_combine_groups_negation(self):
        root, l1 = tree('-a + a,1')
        a0, a1 = root

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), -l1, +a0, a0,
                                                       l1, a1, a1))])

    def test_match_combine_groups_single_const(self):
        root, l1 = tree('a + 2a,1')
        a0, mul = root
        l2, a1 = mul

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l1, a0, a0,
                                                       l2, a1, mul))])

    def test_match_combine_groups_two_const(self):
        ((l2, a0), b), (l3, a1) = (m0, b), m1 = root = tree('2a + b + 3a')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l2, a0, m0,
                                                       l3, a1, m1))])

    def test_match_combine_groups_n_const(self):
        ((l2, a0), (l3, a1)), (l4, a2) = (m0, m1), m2 = root = tree('2a+3a+4a')

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l2, a0, m0,
                                                       l3, a1, m1)),
                 P(root, combine_groups, (Scope(root), l2, a0, m0,
                                                       l4, a2, m2)),
                 P(root, combine_groups, (Scope(root), l3, a1, m1,
                                                       l4, a2, m2))])

    def test_match_combine_groups_identifier_group_no_const(self):
        root, l1 = tree('ab + ab,1')
        ab0, ab1 = root

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l1, ab0, ab0,
                                                       l1, ab1, ab1))])

    def test_match_combine_groups_identifier_group_single_const(self):
        root, l1 = tree('ab + 2ab,1')
        m0, m1 = root
        (l2, a), b = m1

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l1, m0, m0,
                                                       l2, a * b, m1))])

    def test_match_combine_groups_identifier_group_unordered(self):
        root, l1 = tree('ab + ba,1')
        m0, m1 = root
        b, a = m1

        possibilities = match_combine_groups(root)
        self.assertEqualPos(possibilities,
                [P(root, combine_groups, (Scope(root), l1, m0, m0,
                                                       l1, b * a, m1))])

    def test_combine_groups_simple(self):
        root, l1 = tree('a + a,1')
        a0, a1 = root

        self.assertEqualNodes(combine_groups(root,
                              (Scope(root), l1, a0, a0, l1, a1, a1)),
                              (l1 + 1) * a0)

    def test_combine_groups_nary(self):
        root, l1 = tree('ab + b + ba,1')
        abb, ba = root
        ab, b = abb

        self.assertEqualNodes(combine_groups(root,
                              (Scope(root), l1, ab, ab, l1, ba, ba)),
                              (l1 + 1) * ab + b)
