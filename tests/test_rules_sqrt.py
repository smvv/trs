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
from src.rules.sqrt import is_eliminateable_sqrt, match_reduce_sqrt, \
        quadrant_sqrt, constant_sqrt, split_dividers, \
        extract_sqrt_multiplicant, extract_sqrt_mult_priority
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesSqrt(RulesTestCase):

    def test_is_eliminateable_sqrt(self):
        self.assertFalse(is_eliminateable_sqrt(3))
        self.assertTrue(is_eliminateable_sqrt(4))
        self.assertTrue(is_eliminateable_sqrt(9))
        self.assertTrue(is_eliminateable_sqrt(tree('9')))
        self.assertFalse(is_eliminateable_sqrt(tree('-9')))
        self.assertFalse(is_eliminateable_sqrt(tree('5')))
        self.assertTrue(is_eliminateable_sqrt(tree('a ^ 2')))
        self.assertFalse(is_eliminateable_sqrt(tree('a ^ 3')))
        self.assertFalse(is_eliminateable_sqrt(tree('a')))

    def test_match_reduce_sqrt_none(self):
        root = tree('sqrt(a)')
        self.assertEqualPos(match_reduce_sqrt(root), [])

        root = tree('sqrt(-4)')
        self.assertEqualPos(match_reduce_sqrt(root), [])

    def test_match_reduce_sqrt_quadrant(self):
        root = tree('sqrt(a ^ 2)')
        self.assertEqualPos(match_reduce_sqrt(root), [P(root, quadrant_sqrt)])

    def test_match_reduce_sqrt_constant(self):
        root = tree('sqrt(4)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, constant_sqrt, (2,))])

    def test_match_reduce_sqrt_dividers(self):
        root = tree('sqrt(8)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, split_dividers, (4, 2))])

        root = tree('sqrt(27)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, split_dividers, (9, 3))])

    def test_match_reduce_sqrt_mult_priority(self):
        root = tree('sqrt(9 * 3)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, extract_sqrt_mult_priority, (Scope(root[0]), 9)),
                 P(root, extract_sqrt_multiplicant, (Scope(root[0]), 3))])

    def test_match_reduce_sqrt_mult(self):
        ((l2, x),) = root = tree('sqrt(2x)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, extract_sqrt_multiplicant, (Scope(root[0]), l2)),
                 P(root, extract_sqrt_multiplicant, (Scope(root[0]), x))])

        (((l2, x), y),) = root = tree('sqrt(2xy)')
        self.assertEqualPos(match_reduce_sqrt(root),
                [P(root, extract_sqrt_multiplicant, (Scope(root[0]), l2)),
                 P(root, extract_sqrt_multiplicant, (Scope(root[0]), x)),
                 P(root, extract_sqrt_multiplicant, (Scope(root[0]), y))])

    def test_quadrant_sqrt(self):
        root, expect = tree('sqrt(a ^ 2), a')
        self.assertEqual(quadrant_sqrt(root, ()), expect)

        root, expect = tree('-sqrt(a ^ 2), -a')
        self.assertEqual(quadrant_sqrt(root, ()), expect)

    def test_constant_sqrt(self):
        root = tree('sqrt(4)')
        self.assertEqual(constant_sqrt(root, (2,)), 2)

    def test_split_dividers(self):
        root, expect = tree('sqrt(27), sqrt(9 * 3)')
        self.assertEqual(split_dividers(root, (9, 3)), expect)

    def test_extract_sqrt_multiplicant(self):
        root, expect = tree('sqrt(2x), sqrt(2)sqrt(x)')
        l2, x = mul = root[0]
        self.assertEqual(extract_sqrt_multiplicant(root, (Scope(mul), l2,)),
                         expect)

        root, expect = tree('-sqrt(2x), -sqrt(2)sqrt(x)')
        l2, x = mul = root[0]
        self.assertEqual(extract_sqrt_multiplicant(root, (Scope(mul), l2,)),
                         expect)

        root, expect = tree('sqrt(2xy), sqrt(x)sqrt(2y)')
        (l2, x), y = mul = root[0]
        self.assertEqual(extract_sqrt_multiplicant(root, (Scope(mul), x,)),
                         expect)

    def test_extract_sqrt_mult_priority(self):
        root, expect = tree('sqrt(9 * 3), sqrt(9)sqrt(3)')
        l9, l3 = mul = root[0]
        self.assertEqual(extract_sqrt_mult_priority(root, (Scope(mul), l9,)),
                         expect)
