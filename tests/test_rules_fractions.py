from src.rules.fractions import match_constant_division, division_by_one, \
        division_of_zero, division_by_self, match_add_constant_fractions, \
        equalize_denominators, add_nominators
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesFractions(RulesTestCase):

    def test_match_constant_division(self):
        a, zero = tree('a,0')

        root = a / zero
        with self.assertRaises(ZeroDivisionError) as cm:
            match_constant_division(root)
        self.assertEqual(cm.exception.message, 'Division by zero: a / 0.')

        root = a / 1
        possibilities = match_constant_division(root)
        self.assertEqualPos(possibilities, [P(root, division_by_one, (a,))])

        root = zero / a
        possibilities = match_constant_division(root)
        self.assertEqualPos(possibilities, [P(root, division_of_zero)])

        root = a / a
        possibilities = match_constant_division(root)
        self.assertEqualPos(possibilities, [P(root, division_by_self)])

    def test_division_by_one(self):
        a = tree('a')
        root = a / 1

        self.assertEqualNodes(division_by_one(root, (a,)), a)

    def test_division_of_zero(self):
        a, zero = tree('a,0')
        root = zero / a

        self.assertEqualNodes(division_of_zero(root, ()), zero)

    def test_division_by_self(self):
        a, one = tree('a,1')
        root = a / a

        self.assertEqualNodes(division_by_self(root, ()), one)

    def test_match_add_constant_fractions(self):
        a, b, c, l1, l2, l3, l4 = tree('a,b,c,1,2,3,4')

        n0, n1 = root = l1 / l2 + l3 / l4
        possibilities = match_add_constant_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, equalize_denominators, (n0, n1, 4))])

        (((n0, n1), n2), n3), n4 = root = a + l1 / l2 + b + l3 / l4 + c
        possibilities = match_add_constant_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, equalize_denominators, (n1, n3, 4))])

        n0, n1 = root = l2 / l4 + l3 / l4
        possibilities = match_add_constant_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, add_nominators, (n0, n1))])

        (((n0, n1), n2), n3), n4 = root = a + l2 / l4 + b + l3 / l4 + c
        possibilities = match_add_constant_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, add_nominators, (n1, n3))])

    def test_equalize_denominators(self):
        a, b, l1, l2, l3, l4 = tree('a,b,1,2,3,4')

        n0, n1 = root = l1 / l2 + l3 / l4
        self.assertEqualNodes(equalize_denominators(root, (n0, n1, 4)),
                              l2 / l4 + l3 / l4)

        n0, n1 = root = a / l2 + b / l4
        self.assertEqualNodes(equalize_denominators(root, (n0, n1, 4)),
                              (l2 * a) / l4 + b / l4)

    def test_add_nominators(self):
        a, b, c = tree('a,b,c')
        n0, n1 = root = a / b + c / b

        self.assertEqualNodes(add_nominators(root, (n0, n1)), (a + c) / b)
