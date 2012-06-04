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
from tests.rulestestcase import RulesTestCase as TestCase


class TestLeidenOefenopgaveV12(TestCase):
    def test_1_a(self):
        self.assertRewrite([
            '-5(x^2 - 3x + 6)',
            '-(5x ^ 2 + 5(-3x) + 5 * 6)',
            '-(5x ^ 2 - 5 * 3x + 5 * 6)',
            '-(5x ^ 2 - 15x + 5 * 6)',
            '-(5x ^ 2 - 15x + 30)',
            '-5x ^ 2 - -15x - 30',
            '-5x ^ 2 + 15x - 30',
        ])

    def test_1_d(self):
        self.assertRewrite([
            '(2x + x)x',
            '(2 + 1)xx',
            '3xx',
            '3x ^ (1 + 1)',
            '3x ^ 2',
        ])

    def test_1_e(self):
        self.assertRewrite([
            '-2(6x - 4) ^ 2x',
            '-2(6x - 4)(6x - 4)x',
            '-(2 * 6x + 2(-4))(6x - 4)x',
            '-(12x + 2(-4))(6x - 4)x',
            '-(12x - 8)(6x - 4)x',
            '-(12x - 8)(6xx + (-4)x)',
            '-(12x - 8)(6x ^ (1 + 1) + (-4)x)',
            '-(12x - 8)(6x ^ 2 + (-4)x)',
            '-(12x - 8)(6x ^ 2 - 4x)',
            '-(12x * 6x ^ 2 + 12x(-4x) + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72xx ^ 2 + 12x(-4x) + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ (1 + 2) + 12x(-4x) + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 + 12x(-4x) + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 12x * 4x + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48xx + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48x ^ (1 + 1) + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48x ^ 2 + (-8)6x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48x ^ 2 + (-48)x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48x ^ 2 - 48x ^ 2 + (-8)(-4x))',
            '-(72x ^ 3 - 48x ^ 2 - 48x ^ 2 - 8(-4x))',
            '-(72x ^ 3 - 48x ^ 2 - 48x ^ 2 - -8 * 4x)',
            '-(72x ^ 3 - 48x ^ 2 - 48x ^ 2 - -32x)',
            '-(72x ^ 3 - 48x ^ 2 - 48x ^ 2 + 32x)',
            '-(72x ^ 3 + (1 + 1)(-48x ^ 2) + 32x)',
            '-(72x ^ 3 + 2(-48x ^ 2) + 32x)',
            '-(72x ^ 3 - 2 * 48x ^ 2 + 32x)',
            '-(72x ^ 3 - 96x ^ 2 + 32x)',
            '-72x ^ 3 - -96x ^ 2 - 32x',
            '-72x ^ 3 + 96x ^ 2 - 32x',
        ])

    def test_2_a(self):
        self.assertRewrite([
            '(a ^ 2 * b ^ -1) ^ 3(ab ^ 2)',
            '(a ^ 2 * 1 / b ^ 1) ^ 3 * ab ^ 2',
            '(a ^ 2 * 1 / b) ^ 3 * ab ^ 2',
            '((a ^ 2 * 1) / b) ^ 3 * ab ^ 2',
            '(a ^ 2 / b) ^ 3 * ab ^ 2',
            '(a ^ 2) ^ 3 / b ^ 3 * ab ^ 2',
            'a ^ (2 * 3) / b ^ 3 * ab ^ 2',
            'a ^ 6 / b ^ 3 * ab ^ 2',
            '(a ^ 6 * a) / b ^ 3 * b ^ 2',
            'a ^ (6 + 1) / b ^ 3 * b ^ 2',
            'a ^ 7 / b ^ 3 * b ^ 2',
            '(a ^ 7 * b ^ 2) / b ^ 3',
            'b ^ 2 / b ^ 3 * a ^ 7 / 1',
            'b ^ (2 - 3)a ^ 7 / 1',
            'b ^ (-1)a ^ 7 / 1',
            '1 / b ^ 1 * a ^ 7 / 1',
            '1 / b * a ^ 7 / 1',
            '1 / b * a ^ 7',
            '(1a ^ 7) / b',
            'a ^ 7 / b',
        ])

    def test_2_b(self):
        self.assertRewrite([
            'a^3b^2a^3',
            'a ^ (3 + 3)b ^ 2',
            'a ^ 6 * b ^ 2',
        ])

    #def test_2_c(self):
    #    self.assertRewrite([
    #        'a^5+a^3',
    #        'a ^ 5 + a ^ 3',
    #    ])

    def test_2_d(self):
        self.assertRewrite([
            'a^2+a^2',
            '(1 + 1)a ^ 2',
            '2a ^ 2',
        ])

    def test_2_e(self):
        self.assertRewrite([
            '4b^-2',
            '4 * 1 / b ^ 2',
            '(4 * 1) / b ^ 2',
            '4 / b ^ 2',
        ])

    def test_2_f(self):
        self.assertRewrite([
            '(4b) ^ -2',
            '4 ^ (-2)b ^ (-2)',
            '1 / 4 ^ 2 * b ^ (-2)',
            '1 / 16 * b ^ (-2)',
            '1 / 16 * 1 / b ^ 2',
            '(1 * 1) / (16b ^ 2)',
            '1 / (16b ^ 2)',
        ])
