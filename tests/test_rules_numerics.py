from src.rules.numerics import match_divide_numerics, divide_numerics, \
        add_numerics
from src.possibilities import Possibility as P
from src.node import ExpressionLeaf as L
from tests.rulestestcase import RulesTestCase
from tests.test_rules_poly import tree


class TestRulesNumerics(RulesTestCase):

    def test_match_divide_numerics(self):
        # FIXME: Parser does not recognize floats
        #a, b, i2, i3, i6, f1, f2, f3 = tree('a,b,2,3,6,1.0,2.0,3.0')
        a, b, i2, i3, i6 = tree('a,b,2,3,6')
        f1, f2, f3 = L(1.0), L(2.0), L(3.0)

        root = i6 / i2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, divide_numerics, (6, 2))])

        root = i3 / i2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities, [])

        root = f3 / i2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, divide_numerics, (3.0, 2))])

        root = i3 / f2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, divide_numerics, (3, 2.0))])

        root = f3 / f2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, divide_numerics, (3.0, 2.0))])

        root = i3 / f1
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, divide_numerics, (3, 1))])

        root = a / b
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities, [])

    def test_divide_numerics(self):
        # FIXME: Parser does not recognize floats
        #i2, i3, i6, f2, f3 = tree('2,3,6,2.0,3.0')
        i2, i3, i6 = tree('2,3,6')
        f2, f3 = L(2.0), L(3.0)

        self.assertEqual(divide_numerics(i6 / i2, (6, 2)), 3)
        self.assertEqual(divide_numerics(f3 / i2, (3.0, 2)), 1.5)
        self.assertEqual(divide_numerics(i3 / f2, (3, 2.0)), 1.5)
        self.assertEqual(divide_numerics(f3 / f2, (3.0, 2.0)), 1.5)

    def test_add_numerics(self):
        l0, l1 = tree('1,2')
        self.assertEqual(add_numerics(l0 + l1, (l0, l1, 1, 2)), 3)

    def test_add_numerics(self):
        l0, a, l1 = tree('1,a,2')
        self.assertEqual(add_numerics(l0 + a + l1, (l0, l1, 1, 2)), L(3) + a)
