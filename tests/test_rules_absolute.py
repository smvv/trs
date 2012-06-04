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
from src.rules.absolute import match_factor_out_abs_term, \
        remove_absolute_negation, factor_out_abs_sqrt, absolute_numeric, \
        factor_out_abs_term, factor_out_abs_exponent
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesAbsolute(RulesTestCase):

    def test_match_factor_out_abs_term_negation(self):
        root = tree('|-a|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, remove_absolute_negation)])

    def test_match_factor_out_abs_term_numeric(self):
        root = tree('|2|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, absolute_numeric)])

        root = tree('|a|')
        self.assertEqualPos(match_factor_out_abs_term(root), [])

    def test_match_factor_out_abs_term_mult(self):
        ((a, b),) = (ab,) = root = tree('|ab|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, factor_out_abs_term, (Scope(ab), a)),
                 P(root, factor_out_abs_term, (Scope(ab), b))])

        (((a, b), c),) = (abc,) = root = tree('|abc|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, factor_out_abs_term, (Scope(abc), a)),
                 P(root, factor_out_abs_term, (Scope(abc), b)),
                 P(root, factor_out_abs_term, (Scope(abc), c))])

    def test_match_factor_out_abs_term_sqrt(self):
        root = tree('|sqrt a|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, factor_out_abs_sqrt)])

    def test_match_factor_out_abs_term_exponent(self):
        root = tree('|a ^ 2|')
        self.assertEqualPos(match_factor_out_abs_term(root),
                [P(root, factor_out_abs_exponent)])

        root = tree('|a ^ b|')
        self.assertEqualPos(match_factor_out_abs_term(root), [])

    def test_remove_absolute_negation(self):
        root, expect = tree('|-a|, |a|')
        self.assertEqual(remove_absolute_negation(root, ()), expect)

        root, expect = tree('-|-a|, -|a|')
        self.assertEqual(remove_absolute_negation(root, ()), expect)

    def test_absolute_numeric(self):
        root, expect = tree('|2|, 2')
        self.assertEqual(absolute_numeric(root, ()), expect)

        root, expect = tree('-|2|, -2')
        self.assertEqual(absolute_numeric(root, ()), expect)

    def test_factor_out_abs_term(self):
        root, expect = tree('|abc|, |a||bc|')
        (((a, b), c),) = (abc,) = root
        self.assertEqual(factor_out_abs_term(root, (Scope(abc), a)), expect)

        root, expect = tree('|abc|, |b||ac|')
        (((a, b), c),) = (abc,) = root
        self.assertEqual(factor_out_abs_term(root, (Scope(abc), b)), expect)

        root, expect = tree('-|abc|, -|a||bc|')
        (((a, b), c),) = (abc,) = root
        self.assertEqual(factor_out_abs_term(root, (Scope(abc), a)), expect)

    def test_factor_out_abs_sqrt(self):
        root, expect = tree('|sqrt a|, sqrt|a|')
        self.assertEqual(factor_out_abs_sqrt(root, ()), expect)

        root, expect = tree('-|sqrt a|, -sqrt|a|')
        self.assertEqual(factor_out_abs_sqrt(root, ()), expect)

    def test_factor_out_abs_exponent(self):
        root, expect = tree('|a ^ 2|, |a| ^ 2')
        self.assertEqual(factor_out_abs_exponent(root, ()), expect)

        root, expect = tree('-|a ^ 2|, -|a| ^ 2')
        self.assertEqual(factor_out_abs_exponent(root, ()), expect)
