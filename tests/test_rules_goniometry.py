# vim: set fileencoding=utf-8 :
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
from src.rules.goniometry import match_add_quadrants, add_quadrants, \
        factor_out_quadrant_negation, match_negated_parameter, \
        negated_sinus_parameter, is_pi_frac, negated_cosinus_parameter, \
        match_standard_radian, standard_radian
from src.node import PI, OP_SIN, OP_COS, OP_TAN, sin, cos, tan, Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree
from src.rules import goniometry
import doctest


class TestRulesGoniometry(RulesTestCase):

    def test_doctest(self):
        self.assertEqual(doctest.testmod(m=goniometry)[0], 0)

    def test_match_add_quadrants(self):
        s, c = root = tree('sin^2 t + cos^2 t')
        self.assertEqualPos(match_add_quadrants(root),
                [P(root, add_quadrants, (Scope(root), s, c))])

        c, s = root = tree('cos^2 t + sin^2 t')
        self.assertEqualPos(match_add_quadrants(root),
                [P(root, add_quadrants, (Scope(root), s, c))])

        (s, a), c = root = tree('sin^2 t + a + cos^2 t')
        self.assertEqualPos(match_add_quadrants(root),
                [P(root, add_quadrants, (Scope(root), s, c))])

        (s, c0), c1 = root = tree('sin^2 t + cos^2 t + cos^2 t')
        self.assertEqualPos(match_add_quadrants(root),
                [P(root, add_quadrants, (Scope(root), s, c0)),
                 P(root, add_quadrants, (Scope(root), s, c1))])

        root = tree('sin^2 t + cos^2 y')
        self.assertEqualPos(match_add_quadrants(root), [])

        root = tree('sin^2 t - cos^2 t')
        self.assertEqualPos(match_add_quadrants(root), [])

        s, c = root = tree('-sin^2 t - cos^2 t')
        self.assertEqualPos(match_add_quadrants(root),
                [P(root, factor_out_quadrant_negation, (Scope(root), s, c))])

    def test_add_quadrants(self):
        s, c = root = tree('sin(t) ^ 2 + cos(t) ^ 2')
        self.assertEqual(add_quadrants(root, (Scope(root), s, c)), 1)

        root, expect = tree('cos(t) ^ 2 + a + sin(t) ^ 2, a + 1')
        (c, a), s = root
        self.assertEqual(add_quadrants(root, (Scope(root), s, c)), expect)

    def test_factor_out_quadrant_negation(self):
        r, e = tree('-sin(t) ^ 2 - cos(t) ^ 2, -(sin(t) ^ 2 + cos(t) ^ 2)')
        s, c = r
        self.assertEqual(factor_out_quadrant_negation(r, (Scope(r), s, c)), e)

    def test_match_negated_parameter(self):
        s, c = tree('sin -t, cos -t')
        t = s[0]

        self.assertEqualPos(match_negated_parameter(s), \
                [P(s, negated_sinus_parameter, (t,))])

        self.assertEqualPos(match_negated_parameter(c), \
                [P(c, negated_cosinus_parameter, (t,))])

    def test_negated_sinus_parameter(self):
        s = tree('sin -t')
        t = s[0]
        self.assertEqual(negated_sinus_parameter(s, (t,)), -sin(+t))

    def test_negated_cosinus_parameter(self):
        c = tree('cos -t')
        t = c[0]
        self.assertEqual(negated_cosinus_parameter(c, (t,)), cos(+t))

    def test_is_pi_frac(self):
        l1, pi = tree('1,' + PI)

        self.assertTrue(is_pi_frac(l1 / 2 * pi, 2))
        self.assertFalse(is_pi_frac(l1 / 2 * pi, 3))
        self.assertFalse(is_pi_frac(l1 * pi, 3))

    def test_match_standard_radian(self):
        s, c, t = tree('sin(1 / 6 * pi), cos(1 / 2 * pi), tan(0)')

        self.assertEqualPos(match_standard_radian(s), \
                [P(s, standard_radian, (OP_SIN, 1))])

        self.assertEqualPos(match_standard_radian(c), \
                [P(c, standard_radian, (OP_COS, 4))])

        self.assertEqualPos(match_standard_radian(t), \
                [P(t, standard_radian, (OP_TAN, 0))])

    def test_standard_radian(self):
        l0, l1, sq3, pi6, pi4, pi2 = tree('0,1,sqrt(3),1/6*pi,1/4*pi,1/2*pi')

        self.assertEqual(standard_radian(sin(pi6), (OP_SIN, 1)), l1 / 2)
        self.assertEqual(standard_radian(sin(pi2), (OP_SIN, 4)), 1)
        self.assertEqual(standard_radian(cos(l0), (OP_COS, 0)), 1)
        self.assertEqual(standard_radian(tan(pi4), (OP_TAN, 3)), sq3)
