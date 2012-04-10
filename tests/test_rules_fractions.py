from src.rules.fractions import match_constant_division, division_by_one, \
        division_of_zero, division_by_self, match_add_fractions, \
        equalize_denominators, add_nominators, match_multiply_fractions, \
        multiply_fractions, multiply_with_fraction, match_divide_fractions, \
        divide_fraction, divide_by_fraction, match_equal_fraction_parts, \
        constant_to_fraction, extract_fraction_terms
from src.node import Scope
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
        self.assertEqualPos(possibilities, [P(root, division_of_zero, (a,))])

        root = a / a
        possibilities = match_constant_division(root)
        self.assertEqualPos(possibilities, [P(root, division_by_self, (a,))])

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

    def test_match_add_fractions(self):
        a, b, c, l1, l2, l3, l4 = tree('a,b,c,1,2,3,4')

        n0, n1 = root = l1 / l2 + l3 / l4
        possibilities = match_add_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, equalize_denominators, (Scope(root), n0, n1, 4)),
                 P(root, equalize_denominators, (Scope(root), n0, n1, 8))])

        (((n0, n1), n2), n3), n4 = root = a + l1 / l2 + b + l3 / l4 + c
        possibilities = match_add_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, equalize_denominators, (Scope(root), n1, n3, 4)),
                 P(root, equalize_denominators, (Scope(root), n1, n3, 8))])

        n0, n1 = root = l2 / l4 + l3 / l4
        possibilities = match_add_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, add_nominators, (Scope(root), n0, n1))])

        (((n0, n1), n2), n3), n4 = root = a + l2 / l4 + b + l3 / l4 + c
        possibilities = match_add_fractions(root)
        self.assertEqualPos(possibilities,
                [P(root, add_nominators, (Scope(root), n1, n3))])

    def test_match_add_fractions_constant_to_fraction(self):
        l23, l1 = root = tree('2 / 3 + 1')
        self.assertEqualPos(match_add_fractions(root),
                [P(root, constant_to_fraction, (Scope(root), l23, l1))])

    def test_add_fractions_with_negation(self):
        a, b, c, l1, l2, l3, l4 = tree('a,b,c,1,2,3,4')

        (((n0, n1), n2), n3), n4 = root = a + l2 / l2 + b + (-l3 / l4) + c
        self.assertEqualPos(match_add_fractions(root),
                [P(root, equalize_denominators, (Scope(root), n1, n3, 4)),
                 P(root, equalize_denominators, (Scope(root), n1, n3, 8))])

        n0, n1 = root = l1 / l2 + l4 / l3
        self.assertEqualPos(match_add_fractions(root),
                [P(root, equalize_denominators, (Scope(root), n0, n1, 6))])

        (((n0, n1), n2), n3), n4 = root = a + l2 / l4 + b + (-l3 / l4) + c
        self.assertEqualPos(match_add_fractions(root),
                [P(root, add_nominators, (Scope(root), n1, n3))])

    def test_equalize_denominators(self):
        a, b, l1, l2, l3, l4 = tree('a,b,1,2,3,4')

        n0, n1 = root = l1 / l2 + l3 / l4
        self.assertEqualNodes(equalize_denominators(root,
                              (Scope(root), n0, n1, 4)), l2 / l4 + l3 / l4)

        n0, n1 = root = a / l2 + b / l4
        self.assertEqualNodes(equalize_denominators(root,
                              (Scope(root), n0, n1, 4)), (l2 * a) / l4 + b /
                              l4)

        #2 / 2 - 3 / 4  ->  4 / 4 - 3 / 4  # Equalize denominators
        n0, n1 = root = l1 / l2 + (-l3 / l4)
        self.assertEqualNodes(equalize_denominators(root,
            (Scope(root), n0, n1, 4)), l2 / l4 + (-l3 / l4))

        #2 / 2 - 3 / 4  ->  4 / 4 - 3 / 4  # Equalize denominators
        n0, n1 = root = a / l2 + (-b / l4)
        self.assertEqualNodes(equalize_denominators(root,
            (Scope(root), n0, n1, 4)), (l2 * a) / l4 + (-b / l4))

    def test_add_nominators(self):
        a, b, c = tree('a,b,c')
        n0, n1 = root = a / b + c / b
        self.assertEqualNodes(add_nominators(root, (Scope(root), n0, n1)),
                              (a + c) / b)

        n0, n1 = root = a / b + -c / b
        self.assertEqualNodes(add_nominators(root, (Scope(root), n0, n1)),
                              (a + -c) / b)

        n0, n1 = root = a / b + -(c / b)
        self.assertEqualNodes(add_nominators(root, (Scope(root), n0, n1)),
                              (a + -c) / b)

        n0, n1 = root = a / -b + c / -b
        self.assertEqualNodes(add_nominators(root, (Scope(root), n0, n1)),
                              (a + c) / -b)

        n0, n1 = root = a / -b + -c / -b
        self.assertEqualNodes(add_nominators(root, (Scope(root), n0, n1)),
                              (a + -c) / -b)

    def test_constant_to_fraction(self):
        root, e = tree('2 / 3 + 1, 2 / 3 + 3 / 3 * 1')
        l23, l1 = root
        self.assertEqual(constant_to_fraction(root, (Scope(root), l23, l1)), e)

    def test_match_multiply_fractions(self):
        (a, b), (c, d) = ab, cd = root = tree('a / b * (c / d)')
        self.assertEqualPos(match_multiply_fractions(root),
                [P(root, multiply_fractions, (Scope(root), ab, cd))])

        (ab, e), cd = root = tree('4 / b * 2 * (3 / d)')
        self.assertEqualPos(match_multiply_fractions(root),
                [P(root, multiply_fractions, (Scope(root), ab, cd)),
                 P(root, multiply_with_fraction, (Scope(root), ab, e)),
                 P(root, multiply_with_fraction, (Scope(root), cd, e))])

        ab, c = root = tree('1 / sqrt(3) * 2')
        self.assertEqualPos(match_multiply_fractions(root),
                [P(root, multiply_with_fraction, (Scope(root), ab, c))])

    def test_multiply_fractions(self):
        (a, b), (c, d) = ab, cd = root = tree('a / b * (c / d)')
        self.assertEqual(multiply_fractions(root, (Scope(root), ab, cd)),
                         a * c / (b * d))

        (ab, e), cd = root = tree('a / b * e * (c / d)')
        self.assertEqual(multiply_fractions(root, (Scope(root), ab, cd)),
                         a * c / (b * d) * e)

    def test_match_divide_fractions(self):
        (a, b), c = root = tree('a / b / c')
        self.assertEqualPos(match_divide_fractions(root),
                [P(root, divide_fraction, (a, b, c))])

        root = tree('a / (b / c)')
        self.assertEqualPos(match_divide_fractions(root),
                [P(root, divide_by_fraction, (a, b, c))])

    def test_divide_fraction(self):
        (a, b), c = root = tree('a / b / c')
        self.assertEqual(divide_fraction(root, (a, b, c)), a / (b * c))

    def test_divide_by_fraction(self):
        a, (b, c) = root = tree('a / (b / c)')
        self.assertEqual(divide_by_fraction(root, (a, b, c)), a * c / b)

    def test_match_equal_fraction_parts(self):
        root, a, b, c = tree('ab / (ca), a, b, c')
        n, d = root
        self.assertEqualPos(match_equal_fraction_parts(root),
                [P(root, extract_fraction_terms, (Scope(n), Scope(d), a, a))])

        n, d = root = tree('ab / a')
        self.assertEqualPos(match_equal_fraction_parts(root),
                [P(root, extract_fraction_terms, (Scope(n), Scope(d), a, a))])

        n, d = root = tree('a / (ab)')
        self.assertEqualPos(match_equal_fraction_parts(root),
                [P(root, extract_fraction_terms, (Scope(n), Scope(d), a, a))])

        n, d = root = tree('abc / (cba)')
        self.assertEqualPos(match_equal_fraction_parts(root),
                [P(root, extract_fraction_terms, (Scope(n), scope(d), a, a)),
                 P(root, extract_fraction_terms, (Scope(n), scope(d), b, b)),
                 P(root, extract_fraction_terms, (Scope(n), scope(d), c, c))])

        root = tree('a / a')
        self.assertEqualPos(match_equal_fraction_parts(root), [])

        (ap, b), aq = root = tree('a ^ p * b / a ^ q')
        self.assertequalpos(match_equal_fraction_parts(root),
                [p(root, extract_fraction_terms, (a, [ap, b], [aq], 0, 0))])

        (a, b), aq = root = tree('a * b / a ^ q')
        self.assertequalpos(match_equal_fraction_parts(root),
                [p(root, extract_fraction_terms, (a, [a, b], [aq], 0, 0))])

        (ap, b), a = root = tree('a ^ p * b / a')
        self.assertequalpos(match_equal_fraction_parts(root),
                [p(root, extract_fraction_terms, (a, [ap, b], [a], 0, 0))])

    #def test_match_equal_fraction_parts(self):
    #    (a, b), (c, a) = root = tree('ab / (ca)')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, divide_fraction_parts, (a, [a, b], [c, a], 0, 1))])

    #    (a, b), a = root = tree('ab / a')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, divide_fraction_parts, (a, [a, b], [a], 0, 0))])

    #    a, (a, b) = root = tree('a / (ab)')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, divide_fraction_parts, (a, [a], [a, b], 0, 0))])

    #    root = tree('abc / (cba)')
    #    ((a, b), c) = root[0]
    #    s0, s1 = [a, b, c], [c, b, a]
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, divide_fraction_parts, (a, s0, s1, 0, 2)),
    #             P(root, divide_fraction_parts, (b, s0, s1, 1, 1)),
    #             P(root, divide_fraction_parts, (c, s0, s1, 2, 0))])

    #    root = tree('-a / a')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, divide_fraction_parts, (a, [-a], [a], 0, 0))])

    #    (ap, b), aq = root = tree('a ^ p * b / a ^ q')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, extract_divided_roots, (a, [ap, b], [aq], 0, 0))])

    #    (a, b), aq = root = tree('a * b / a ^ q')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, extract_divided_roots, (a, [a, b], [aq], 0, 0))])

    #    (ap, b), a = root = tree('a ^ p * b / a')
    #    self.assertEqualPos(match_equal_fraction_parts(root),
    #            [P(root, extract_divided_roots, (a, [ap, b], [a], 0, 0))])

    #def test_divide_fraction_parts(self):
    #    (a, b), (c, a) = root = tree('ab / (ca)')
    #    result = divide_fraction_parts(root, (a, [a, b], [c, a], 0, 1))
    #    self.assertEqual(result, b / c)

    #    (a, b), a = root = tree('ab / a')
    #    result = divide_fraction_parts(root, (a, [a, b], [a], 0, 0))
    #    self.assertEqual(result, b / 1)

    #    root, l1 = tree('a / (ab), 1')
    #    a, (a, b) = root
    #    result = divide_fraction_parts(root, (a, [a], [a, b], 0, 0))
    #    self.assertEqual(result, l1 / b)

    #    root = tree('abc / (cba)')
    #    ((a, b), c) = root[0]
    #    result = divide_fraction_parts(root, (a, [a, b, c], [c, b, a], 0, 2))
    #    self.assertEqual(result, b * c / (c * b))
    #    result = divide_fraction_parts(root, (b, [a, b, c], [c, b, a], 1, 1))
    #    self.assertEqual(result, a * c / (c * a))
    #    result = divide_fraction_parts(root, (c, [a, b, c], [c, b, a], 2, 0))
    #    self.assertEqual(result, a * b / (b * a))

    #    (a, b), a = root = tree('-ab / a')
    #    result = divide_fraction_parts(root, (a, [-a, b], [a], 0, 0))
    #    self.assertEqual(result, -b / 1)

    #def test_extract_divided_roots(self):
    #    r, a = tree('a ^ p * b / a ^ q, a')
    #    ((a, p), b), (a, q) = (ap, b), aq = r
    #    self.assertEqual(extract_divided_roots(r, (a, [ap, b], [aq], 0, 0)),
    #                     a ** p / a ** q * b / 1)

    #    r = tree('a * b / a ^ q, a')
    #    self.assertEqual(extract_divided_roots(r, (a, [a, b], [aq], 0, 0)),
    #                     a / a ** q * b / 1)

    #    r = tree('a ^ p * b / a, a')
    #    self.assertEqual(extract_divided_roots(r, (a, [ap, b], [a], 0, 0)),
    #                     a ** p / a * b / 1)
