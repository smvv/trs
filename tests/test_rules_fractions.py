# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
from src.rules.fractions import match_constant_division, division_by_one, \
        division_of_zero, division_by_self, match_add_fractions, \
        equalize_denominators, add_nominators, match_multiply_fractions, \
        multiply_fractions, multiply_with_fraction, match_divide_fractions, \
        divide_fraction, divide_by_fraction, match_extract_fraction_terms, \
        constant_to_fraction, extract_nominator_term, extract_fraction_terms, \
        match_division_in_denominator, multiply_with_term, \
        divide_fraction_by_term, match_combine_fractions, combine_fractions, \
        match_remove_division_negation, remove_division_negation, \
        match_fraction_in_division, fraction_in_division
from src.node import ExpressionNode as N, Scope, OP_MUL
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
        root, e = tree('2 / 3 + 1, 2 / 3 + (3 * 1) / 3')
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

        (a, b), c = root = tree('-a / b / c')
        self.assertEqual(divide_fraction(root, (a, b, c)), -(a / (b * c)))

        root = tree('a / b / -c')
        self.assertEqual(divide_fraction(root, (a, b, c)), a / (b * -c))

    def test_divide_by_fraction(self):
        a, (b, c) = root = tree('a / (b / c)')
        self.assertEqual(divide_by_fraction(root, (a, b, c)), a * c / b)

        a, (b, c) = root = tree('-a / (b / c)')
        self.assertEqual(divide_by_fraction(root, (a, b, c)), -(a * c / b))

        root = tree('a / -(b / c)')
        self.assertEqual(divide_by_fraction(root, (a, b, c)), -(a * c / b))

    def test_match_extract_fraction_terms(self):
        root, a, b, c = tree('(ab) / (ca), a, b, c')
        n, d = root
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, divide_fraction_by_term, (Scope(n), Scope(d), a, a))])

        lscp = lambda l: Scope(N(OP_MUL, l))

        n, d = root = tree('(ab) / a')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, divide_fraction_by_term, (Scope(n), lscp(d), a, a))])

        n, d = root = tree('a / (ab)')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, divide_fraction_by_term, (lscp(n), Scope(d), a, a))])

        n, d = root = tree('(abc) / (cba)')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, divide_fraction_by_term, (Scope(n), Scope(d), a, a)),
                 P(root, divide_fraction_by_term, (Scope(n), Scope(d), b, b)),
                 P(root, divide_fraction_by_term, (Scope(n), Scope(d), c, c))])

        root = tree('a / a')
        self.assertEqualPos(match_extract_fraction_terms(root), [])

        (ap, b), aq = n, d = root = tree('(a ^ p * b) / a ^ q')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_fraction_terms, (Scope(n), lscp(d), ap, aq))])

        (a, b), aq = n, d = root = tree('(ab) / a ^ q')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_fraction_terms, (Scope(n), lscp(d), a, aq))])

        (ap, b), a = n, d = root = tree('(a ^ p * b) / a')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_fraction_terms, (Scope(n), lscp(d), ap, a))])

        (l2, a), l3 = n, d = root = tree('(2a) / 3')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_nominator_term, (2, a))])

        a, l3 = n, d = root = tree('a / 3')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_nominator_term, (1, a))])

        root = tree('(2 * 4) / 3')
        self.assertEqualPos(match_extract_fraction_terms(root), [])

        n, d = root = tree('(2a) / 2')
        self.assertEqualPos(match_extract_fraction_terms(root),
                [P(root, extract_nominator_term, (2, a)),
                 P(root, divide_fraction_by_term, (Scope(n), lscp(d), 2, 2))])

    def test_extract_nominator_term(self):
        root, expect = tree('(2a) / 3, 2 / 3 * a')
        l2, a = root[0]
        self.assertEqual(extract_nominator_term(root, (l2, a)), expect)

        root, expect, l1 = tree('a / 3, 1 / 3 * a, 1')
        self.assertEqual(extract_nominator_term(root, (l1, root[0])), expect)

    def test_extract_fraction_terms_basic(self):
        root, expect = tree('(ab) / (ca), a / a * b / c')
        n, d = root
        self.assertEqual(extract_fraction_terms(root,
                (Scope(n), Scope(d), n[0], d[1])), expect)

    def test_extract_fraction_terms_leaf(self):
        root, expect = tree('(ba) / a, a / a * b / 1')
        n, d = root
        self.assertEqual(extract_fraction_terms(root,
                (Scope(n), Scope(N(OP_MUL, d)), n[1], d)), expect)

        root, expect = tree('a / (ab), a / a * 1 / b')
        n, d = root
        self.assertEqual(extract_fraction_terms(root,
                (Scope(N(OP_MUL, n)), Scope(d), n, d[0])), expect)

    def test_extract_fraction_terms_chain(self):
        self.assertRewrite([
            '(a ^ 3 * 4) / (a ^ 2 * 5)',
            'a ^ 3 / a ^ 2 * 4 / 5',
            'a ^ (3 - 2)4 / 5',
            'a ^ 1 * 4 / 5',
            'a * 4 / 5',
            # FIXME: '4 / 5 * a',
        ])

    def test_divide_fraction_by_term(self):
        (ab, a), expect = root = tree('(ab) / a, b')
        args = Scope(ab), Scope(N(OP_MUL, a)), ab[0], a
        self.assertEqual(divide_fraction_by_term(root, args), expect)

    def test_match_division_in_denominator(self):
        a, ((b, c), d) = root = tree('a / (b / c + d)')
        self.assertEqualPos(match_division_in_denominator(root),
                [P(root, multiply_with_term, (c,))])

        a, ((d, (b, c)), e) = root = tree('a / (d + b / c + e)')
        self.assertEqualPos(match_division_in_denominator(root),
                [P(root, multiply_with_term, (c,))])

    def test_multiply_with_term_chain(self):
        self.assertRewrite([
            '1 / (1 / b - 1 / a)',
            '1 / ((1 * -a) / (b * -a) + (b * 1) / (b * -a))',
            '1 / ((1 * -a + b * 1) / (b * -a))',
            '1 / ((-a + b * 1) / (b * -a))',
            '1 / ((-a + b) / (b * -a))',
            '1 / ((-a + b) / (-ba))',
            '1 / (-(-a + b) / (ba))',
            '1 / ((--a - b) / (ba))',
            '1 / ((a - b) / (ba))',
            '(1ba) / (a - b)',
            '(ba) / (a - b)',
            '(ab) / (a - b)',
        ])

    def test_match_combine_fractions(self):
        ab, cd = root = tree('a / b + c / d')
        self.assertEqualPos(match_combine_fractions(root),
                [P(root, combine_fractions, (Scope(root), ab, cd))])

    def test_combine_fractions(self):
        (a, b), (c, d) = ab, cd = root = tree('a / b + c / d')
        self.assertEqual(combine_fractions(root, (Scope(root), ab, cd)),
                         a * d / (b * d) + b * c / (b * d))

    def test_match_remove_division_negation(self):
        root = tree('-(-a + b) / c')
        self.assertEqualPos(match_remove_division_negation(root),
                [P(root, remove_division_negation, (True, root[0]))])

        root = tree('-a / (-b + c)')
        self.assertEqualPos(match_remove_division_negation(root),
                [P(root, remove_division_negation, (False, root[1]))])

    def test_remove_division_negation(self):
        (a, b), c = root = tree('-(-a + b) / c')
        self.assertEqual(remove_division_negation(root, (True, root[0])),
                         (-a - b) / c)

        a, (b, c) = root = tree('-a / (-b + c)')
        self.assertEqual(remove_division_negation(root, (False, root[1])),
                         +a / (-b - c))

    def test_match_fraction_in_division(self):
        (fr, b), c = root = tree('(1 / a * b) / c')
        self.assertEqualPos(match_fraction_in_division(root),
                [P(root, fraction_in_division, (True, Scope(root[0]), fr))])

        c, (fr, b) = root = tree('c / (1 / a * b)')
        self.assertEqualPos(match_fraction_in_division(root),
                [P(root, fraction_in_division, (False, Scope(root[1]), fr))])

        (fr0, b), (fr1, d) = root = tree('(1 / a * b) / (1 / c * d)')
        self.assertEqualPos(match_fraction_in_division(root),
                [P(root, fraction_in_division, (True, Scope(root[0]), fr0)),
                 P(root, fraction_in_division, (False, Scope(root[1]), fr1))])

    def test_fraction_in_division(self):
        root, expected = tree('(1 / a * b) / c, b / (ac)')
        self.assertEqual(fraction_in_division(root,
            (True, Scope(root[0]), root[0][0])), expected)

        root, expected = tree('c / (1 / a * b), (ac) / b')
        self.assertEqual(fraction_in_division(root,
            (False, Scope(root[1]), root[1][0])), expected)

        root, expected = tree('c / (-(1 / a) * b), (ac) / ((-1)b)')
        self.assertEqual(fraction_in_division(root,
            (False, Scope(root[1]), root[1][0])), expected)

        root, expected = tree('c / ((-1) / a * b), (ac) / ((-1)b)')
        self.assertEqual(fraction_in_division(root,
            (False, Scope(root[1]), root[1][0])), expected)

        root, expected = tree('c / (1 / (-a) * b), ((-a)c) / b')
        self.assertEqual(fraction_in_division(root,
            (False, Scope(root[1]), root[1][0])), expected)
