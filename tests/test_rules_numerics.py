from src.rules.numerics import add_numerics, match_divide_numerics, \
        divide_numerics, match_multiply_numerics, multiply_numerics
from src.possibilities import Possibility as P
from src.node import ExpressionLeaf as L
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNumerics(RulesTestCase):

    def test_add_numerics(self):
        l0, a, l1 = tree('1,a,2')

        self.assertEqual(add_numerics(l0 + l1, (l0, l1, L(1), L(2))), 3)
        self.assertEqual(add_numerics(l0 + a + l1, (l0, l1, L(1), L(2))),
                         L(3) + a)

    def test_add_numerics_negations(self):
        l0, a, l1 = tree('1,a,2')

        self.assertEqual(add_numerics(l0 + -l1, (l0, -l1, L(1), -L(2))), -1)
        self.assertEqual(add_numerics(l0 + a + -l1, (l0, -l1, L(1), -L(2))),
                         L(-1) + a)

    def test_match_divide_numerics(self):
        a, b, i2, i3, i6, f1, f2, f3 = tree('a,b,2,3,6,1.0,2.0,3.0')

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
        i2, i3, i6, f2, f3 = tree('2,3,6,2.0,3.0')

        self.assertEqual(divide_numerics(i6 / i2, (6, 2)), 3)
        self.assertEqual(divide_numerics(f3 / i2, (3.0, 2)), 1.5)
        self.assertEqual(divide_numerics(i3 / f2, (3, 2.0)), 1.5)
        self.assertEqual(divide_numerics(f3 / f2, (3.0, 2.0)), 1.5)

    def test_match_multiply_numerics(self):
        i2, i3, i6, f2, f3, f6 = tree('2,3,6,2.0,3.0,6.0')

        root = i3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (i3, i2, 3, 2))])

        root = f3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (f3, i2, 3.0, 2))])

        root = i3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (i3, f2, 3, 2.0))])

        root = f3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (f3, f2, 3.0, 2.0))])

    def test_multiply_numerics(self):
        a, b, i2, i3, i6, f2, f3, f6 = tree('a,b,2,3,6,2.0,3.0,6.0')

        self.assertEqual(multiply_numerics(i3 * i2, (i3, i2, 3, 2)), 6)
        self.assertEqual(multiply_numerics(f3 * i2, (f3, i2, 3.0, 2)), 6.0)
        self.assertEqual(multiply_numerics(i3 * f2, (i3, f2, 3, 2.0)), 6.0)
        self.assertEqual(multiply_numerics(f3 * f2, (f3, f2, 3.0, 2.0)), 6.0)

        self.assertEqualNodes(multiply_numerics(a * i3 * i2 * b, (i3, i2, 3, 2)),
                              a * 6 * b)

    def test_multiply_numerics_negation(self):
        l1_neg, l2 = root = tree('-1 * 2')
        self.assertEqualNodes(multiply_numerics(root, (l1_neg, l2, -1, 2)), -l2)

        root, l6 = tree('1 - 2 * 3,6')
        l1, neg = root
        l2, l3 = mul = neg[0]
        self.assertEqualNodes(multiply_numerics(mul, (l2, l3, 2, 3)), l6)

        l1, mul = root = tree('1 + -2 * 3')
        l2_neg, l3 = mul
        self.assertEqualNodes(multiply_numerics(mul, (l2_neg, l3, -2, 3)), -l6)

        root, l30 = tree('-5 * x ^ 2 - -15x - 5 * 6,30')
        rest, mul_neg = root
        l5_neg, l6 = mul = mul_neg[0]
        self.assertEqualNodes(multiply_numerics(mul, (l5_neg, l6, 5, 6)), l30)
