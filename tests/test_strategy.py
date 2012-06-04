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
from src.rules.factors import expand_double, expand_single
from src.node import Scope
from src.possibilities import Possibility as P
from src.strategy import find_possibilities
from tests.rulestestcase import RulesTestCase, tree


class TestStrategy(RulesTestCase):

    def test_find_possibilities_sort(self):
        (ab, cd), e = root = tree('(a + b)(c + d)e')
        self.assertEqualPos(find_possibilities(root),
                [P(root, expand_single, (Scope(root), cd, e)),
                 P(root, expand_single, (Scope(root), ab, e)),
                 P(root, expand_double, (Scope(root), ab, cd))])
