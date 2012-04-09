from src.rules.numerics import match_add_numerics, add_numerics, \
        match_divide_numerics, divide_numerics, reduce_fraction_constants, \
        match_multiply_numerics, multiply_numerics, \
        raise_numerics
from src.node import ExpressionLeaf as L, Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNumerics(RulesTestCase):

    def test_match_add_numerics(self):
        l1, l2 = root = tree('1 + 2')
        possibilities = match_add_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (Scope(root), l1, l2))])

        (l1, b), l2 = root = tree('1 + b + 2')
        possibilities = match_add_numerics(root)
        self.assertEqualPos(possibilities,
                [P(root, add_numerics, (Scope(root), l1, l2))])

    def test_add_numerics(self):
        l0, a, l1 = tree('1,a,2')

        root = l0 + l1
        self.assertEqual(add_numerics(root, (Scope(root), l0, l1)), 3)
        root = l0 + a + l1
        self.assertEqual(add_numerics(root, (Scope(root), l0, l1)), L(3) + a)

    def test_add_numerics_negations(self):
        l1, a, l2 = tree('1,a,2')
        ml1, ml2 = -l1, -l2

        r = ml1 + l2
        self.assertEqual(add_numerics(r, (Scope(r), ml1, l2)), 1)
        r = l1 + ml2
        self.assertEqual(add_numerics(r, (Scope(r), l1, ml2)), -1)

    def test_match_divide_numerics(self):
        a, b, i2, i3, i4, i6, f1, f2, f3 = tree('a,b,2,3,4,6,1.0,2.0,3.0')

        root = i6 / i2
        possibilities = match_divide_numerics(root)
        self.assertEqualPos(possibilities, [P(root, divide_numerics)])

        root = -i6 / i2
        self.assertEqualPos(match_divide_numerics(root), [])

        root = i6 / -i2
        self.assertEqualPos(match_divide_numerics(root), [])

        root = i2 / i4
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, reduce_fraction_constants, (2,))])

        root = f3 / i2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = i3 / f2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = f3 / f2
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = i3 / f1
        self.assertEqualPos(match_divide_numerics(root),
                [P(root, divide_numerics)])

        root = a / b
        self.assertEqualPos(match_divide_numerics(root), [])

    def test_divide_numerics(self):
        i2, i3, i6, f2, f3 = tree('2,3,6,2.0,3.0')

        self.assertEqual(divide_numerics(i6 / i2, ()), 3)
        self.assertEqual(divide_numerics(f3 / i2, ()), 1.5)
        self.assertEqual(divide_numerics(i3 / f2, ()), 1.5)
        self.assertEqual(divide_numerics(f3 / f2, ()), 1.5)
        self.assertEqual(divide_numerics(-(i6 / i2), ()), -i3)

    def test_reduce_fraction_constants(self):
        l1, l2 = tree('1,2')
        self.assertEqual(reduce_fraction_constants(l2 / 4, (2,)), l1 / l2)

    #def test_fraction_to_int_fraction(self):
    #    l1, l4 = tree('1,4')
    #    self.assertEqual(fraction_to_int_fraction(l4 / 3, (1, 1, 3)),
    #                     l1 + l1 / 3)

    def test_match_multiply_numerics(self):
        i2, i3, i6, f2, f3, f6 = tree('2,3,6,2.0,3.0,6.0')

        root = i3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), i3, i2))])

        root = f3 * i2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), f3, i2))])

        root = i3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), i3, f2))])

        root = f3 * f2
        self.assertEqual(match_multiply_numerics(root),
                [P(root, multiply_numerics, (Scope(root), f3, f2))])

    def test_multiply_numerics(self):
        a, b, i2, i3, i6, f2, f3, f6 = tree('a,b,2,3,6,2.0,3.0,6.0')

        root = i3 * i2
        self.assertEqual(multiply_numerics(root, (Scope(root), i3, i2)), 6)
        root = f3 * i2
        self.assertEqual(multiply_numerics(root, (Scope(root), f3, i2)), 6.0)
        root = i3 * f2
        self.assertEqual(multiply_numerics(root, (Scope(root), i3, f2)), 6.0)
        root = f3 * f2
        self.assertEqual(multiply_numerics(root, (Scope(root), f3, f2)), 6.0)

        root = a * i3 * i2 * b
        self.assertEqualNodes(multiply_numerics(root,
                              (Scope(root), i3, i2)), a * 6 * b)

    def test_multiply_numerics_negation(self):
        l1_neg, l2 = root = tree('-1 * 2')
        self.assertEqualNodes(multiply_numerics(root, (Scope(root), l1_neg,
                                                      l2)), -l2)

        root, l6 = tree('1 + -2 * 3,6')
        l1, mul = root
        l2_neg, l3 = mul
        self.assertEqualNodes(multiply_numerics(mul, (Scope(mul),
                                                      l2_neg, l3)), -l6)

        root, l30 = tree('-5 * x ^ 2 - -15x - 5 * 6,30')
        rest, mul = root
        l5_neg, l6 = mul
        self.assertEqualNodes(multiply_numerics(mul, (Scope(mul),
                                                      l5_neg, l6)), -l30)

    def test_raise_numerics(self):
        l1, l2 = root = tree('2 ^ 3')
        self.assertEqualNodes(raise_numerics(root, (l1, l2)), L(8))

        l1_neg, l2 = root = tree('(-2) ^ 2')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2)), --L(4))

        l1_neg, l2 = root = tree('(-2) ^ 3')
        self.assertEqualNodes(raise_numerics(root, (l1_neg, l2)), ---L(8))
