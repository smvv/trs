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
from src.rules.powers import match_add_exponents, add_exponents, \
        match_subtract_exponents, subtract_exponents, \
        match_multiply_exponents, multiply_exponents, \
        match_duplicate_exponent, duplicate_exponent, \
        match_raised_fraction, raised_fraction, \
        match_remove_negative_child, remove_negative_exponent, \
        remove_negative_root, match_exponent_to_root, exponent_to_root, \
        match_constant_exponent, remove_power_of_zero, remove_power_of_one
from src.node import Scope, ExpressionNode as N
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesPowers(RulesTestCase):

    def test_match_add_exponents_binary(self):
        a, p, q = tree('a,p,q')
        n0, n1 = root = a ** p * a ** q

        possibilities = match_add_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, add_exponents, (Scope(root), n0, n1, a, p, q))])

    def test_match_add_exponents_ternary(self):
        a, p, q, r = tree('a,p,q,r')
        (n0, n1), n2 = root = a ** p * a ** q * a ** r

        possibilities = match_add_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, add_exponents, (Scope(root), n0, n1, a, p, q)),
                 P(root, add_exponents, (Scope(root), n0, n2, a, p, r)),
                 P(root, add_exponents, (Scope(root), n1, n2, a, q, r))])

    def test_match_add_exponents_multiple_identifiers(self):
        a, b, p, q = tree('a,b,p,q')
        ((a0, b0), a1), b1 = root = a ** p * b ** p * a ** q * b ** q

        possibilities = match_add_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, add_exponents, (Scope(root), a0, a1, a, p, q)),
                 P(root, add_exponents, (Scope(root), b0, b1, b, p, q))])

    def test_match_add_exponents_nary_multiplication(self):
        a, p, q = tree('a,p,q')
        (n0, l1), n1 = root = a ** p * 2 * a ** q

        possibilities = match_add_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, add_exponents, (Scope(root), n0, n1, a, p, q))])

    def test_match_add_exponents_negated(self):
        a, q = tree('a,q')
        n0, n1 = root = (-a) * a ** q

        possibilities = match_add_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, add_exponents, (Scope(root), n0, n1, a, 1, q))])

    def test_match_subtract_exponents_powers(self):
        a, p, q = tree('a,p,q')
        root = a ** p / a ** q

        possibilities = match_subtract_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, subtract_exponents, (a, p, q))])

    def test_match_subtract_power_id(self):
        a, p = tree('a,p')
        root = a ** p / a

        possibilities = match_subtract_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, subtract_exponents, (a, p, 1))])

    def test_match_subtract_id_power(self):
        a, q = tree('a,q')
        root = a / a ** q

        possibilities = match_subtract_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, subtract_exponents, (a, 1, q))])

    def test_match_multiply_exponents(self):
        a, p, q = tree('a,p,q')
        root = (a ** p) ** q

        possibilities = match_multiply_exponents(root)
        self.assertEqualPos(possibilities,
                [P(root, multiply_exponents, (a, p, q))])

    def test_match_duplicate_exponent(self):
        a, b, p = tree('a,b,p')
        root = (a * b) ** p

        possibilities = match_duplicate_exponent(root)
        self.assertEqualPos(possibilities,
                [P(root, duplicate_exponent, ([a, b], p))])

    def test_match_raised_fraction(self):
        ab, p = root = tree('(a / b) ^ p')

        self.assertEqualPos(match_raised_fraction(root),
                [P(root, raised_fraction, (ab, p))])

    def test_raised_fraction(self):
        ab, p = root = tree('(a / b) ^ p')
        a, b = ab

        self.assertEqual(raised_fraction(root, (ab, p)), a ** p / b ** p)

    def test_match_remove_negative_child(self):
        root = tree('a ^ -p')
        self.assertEqualPos(match_remove_negative_child(root),
                [P(root, remove_negative_exponent)])

        root = tree('(-a) ^ 3')
        self.assertEqualPos(match_remove_negative_child(root),
                [P(root, remove_negative_root)])

        root = tree('(-a) ^ 2')
        self.assertEqualPos(match_remove_negative_child(root), [])

        root = tree('(-a) ^ -3')
        self.assertEqualPos(match_remove_negative_child(root),
                [P(root, remove_negative_exponent),
                 P(root, remove_negative_root)])

    def test_match_exponent_to_root(self):
        root = tree('a ^ (1 / 2)')
        self.assertEqualPos(match_exponent_to_root(root),
                [P(root, exponent_to_root)])

        root = tree('a ^ (n / 2)')
        self.assertEqualPos(match_exponent_to_root(root),
                [P(root, exponent_to_root)])

    def test_add_exponents(self):
        a, p, q = tree('a,p,q')
        n0, n1 = root = a ** p * a ** q

        self.assertEqualNodes(add_exponents(root,
                              (Scope(root), n0, n1, a, p, q)), a ** (p + q))

    def test_subtract_exponents(self):
        a, p, q = tree('a,p,q')
        root = a ** p / a ** q

        self.assertEqualNodes(subtract_exponents(root, (a, p, q)),
                              a ** (p - q))

    def test_multiply_exponents(self):
        a, p, q = tree('a,p,q')
        root = (a ** p) ** q

        self.assertEqualNodes(multiply_exponents(root, (a, p, q)),
                              a ** (p * q))

    def test_duplicate_exponent(self):
        a, b, c, p = tree('a,b,c,p')

        root = (a * b) ** p
        self.assertEqualNodes(duplicate_exponent(root, ([a, b], p)),
                              a ** p * b ** p)

        root = (a * b * c) ** p
        self.assertEqualNodes(duplicate_exponent(root, ([a, b, c], p)),
                              a ** p * b ** p * c ** p)

    def test_remove_negative_exponent(self):
        a, p, l1 = tree('a,-p,1')
        root = a ** p
        self.assertEqualNodes(remove_negative_exponent(root, ()),
                              l1 / a ** +p)

    def test_remove_negative_root(self):
        root, expect = tree('(-a) ^ 3, -a ^ 3')
        self.assertEqualNodes(remove_negative_root(root, ()), expect)

        root, expect = tree('(-a) ^ -3, -a ^ -3')
        self.assertEqualNodes(remove_negative_root(root, ()), expect)

    def test_exponent_to_root(self):
        root, expect = tree('a ^ (1 / 2), sqrt(a)')
        self.assertEqualNodes(exponent_to_root(root, ()), expect)

        root, expect = tree('a ^ (n / 2), sqrt(a ^ n)')
        self.assertEqualNodes(exponent_to_root(root, ()), expect)

    def test_match_constant_exponent(self):
        a0, a1, a2 = tree('a ^ 0, a ^ 1, a ^ 2')

        self.assertEqualPos(match_constant_exponent(a0),
                            [P(a0, remove_power_of_zero, ())])

        self.assertEqualPos(match_constant_exponent(a1),
                            [P(a1, remove_power_of_one, ())])

        self.assertEqualPos(match_constant_exponent(a2), [])

    def test_remove_power_of_zero(self):
        self.assertEqual(remove_power_of_zero(tree('a0'), ()), 1)

    def test_remove_power_of_one(self):
        a1 = tree('a1')
        self.assertEqual(remove_power_of_one(a1, ()), a1[0])
