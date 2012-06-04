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
from src.rules.negation import match_negated_factor, negated_factor, \
        match_negate_polynome, negate_polynome, negated_zero, \
        double_negation, match_negated_division, negated_nominator, \
        negated_denominator
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesNegation(RulesTestCase):

    def test_match_negated_factor(self):
        a, b = root = tree('a * -b')
        self.assertEqualPos(match_negated_factor(root),
                [P(root, negated_factor, (Scope(root), b))])

        (a, b), c = root = tree('a * (-b) * -c')
        scope = Scope(root)
        self.assertEqualPos(match_negated_factor(root),
                [P(root, negated_factor, (scope, b)),
                 P(root, negated_factor, (scope, c))])

    def test_negated_factor(self):
        a, b = root = tree('a * -b')
        self.assertEqual(negated_factor(root, (Scope(root), b)), -(a * +b))

        (a, b), c = root = tree('a * (-b) * -c')
        self.assertEqual(negated_factor(root, (Scope(root), b)), -(a * +b * c))
        self.assertEqual(negated_factor(root, (Scope(root), c)), -(a * b * +c))

    def test_match_negate_polynome(self):
        root = tree('--a')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, double_negation)])

        root = tree('-0')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, negated_zero)])

        root = tree('--0')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, double_negation),
                 P(root, negated_zero)])

        root = tree('-(a + b)')
        self.assertEqualPos(match_negate_polynome(root),
                [P(root, negate_polynome)])

    def test_double_negation(self):
        root = tree('--a')
        self.assertEqual(double_negation(root, ()), ++root)

    def test_negated_zero(self):
        root = tree('-0')
        self.assertEqual(negated_zero(root, ()), 0)

    def test_negate_polynome(self):
        a, b = root = tree('-(a + b)')
        self.assertEqual(negate_polynome(root, ()), -a + -b)

        a, b = root = tree('-(a - b)')
        self.assertEqual(negate_polynome(root, ()), -a + -b)

    def test_match_negated_division_none(self):
        self.assertEqual(match_negated_division(tree('1 / 2')), [])

    def test_match_negated_division_single(self):
        l1, l2 = root = tree('-1 / 2')
        self.assertEqualPos(match_negated_division(root), [])

        l1, l2 = root = tree('(-1) / 2')
        self.assertEqualPos(match_negated_division(root),
                [P(root, negated_nominator)])

        l1, l2 = root = tree('1 / -2')
        self.assertEqualPos(match_negated_division(root),
                [P(root, negated_denominator)])

    def test_match_negated_division_double(self):
        root = tree('(-1) / -2')
        self.assertEqualPos(match_negated_division(root),
                [P(root, negated_nominator),
                 P(root, negated_denominator)])

    def test_negated_nominator(self):
        l1, l2 = root = tree('(-1) / 2')
        self.assertEqual(negated_nominator(root, ()), -(+l1 / l2))

    def test_negated_denominator(self):
        l1, l2 = root = tree('1 / -2')
        self.assertEqual(negated_denominator(root, ()), -(l1 / +l2))

    def test_double_negated_division(self):
        self.assertRewrite([
            '(-a) / (-b)',
            '-a / (-b)',
            '--a / b',
            'a / b',
        ])
