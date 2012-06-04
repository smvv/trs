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


class TestRewrite(TestCase):

    def test_addition_rewrite(self):
        self.assertRewrite([
            '2 + 3 + 4',
            '5 + 4',
            '9',
        ])

    def test_addition_identifiers_rewrite(self):
        self.assertRewrite([
            '2 + 3a + 4',
            '6 + 3a',
        ])

    def test_division_rewrite(self):
        self.assertRewrite([
            '2/7 - 4/11',
            '22 / 77 - 28 / 77',
            '(22 - 28) / 77',
            '(-6) / 77',
            '-6 / 77',
        ])
