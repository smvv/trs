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
import unittest

from src.possibilities import MESSAGES, Possibility as P, flatten_mult
from tests.rulestestcase import tree

from src.parser import Parser
from tests.parser import ParserWrapper


def dummy_handler(root, args):  # pragma: nocover
    pass


def dummy_handler_msg(root, args):  # pragma: nocover
    pass


MESSAGES[dummy_handler_msg] = 'foo {1} + {2} bar'


class TestPossibilities(unittest.TestCase):

    def setUp(self):
        self.l1, self.l2 = self.n = tree('1 + 2')
        self.p0 = P(self.n, dummy_handler, (self.l1, self.l2))
        self.p1 = P(self.n, dummy_handler_msg, (self.l1, self.l2))

    def test___str__(self):
        self.assertEqual(str(self.p0),
                '<Possibility root="1 + 2" handler=dummy_handler args=(1, 2)>')
        self.assertEqual(str(self.p1), 'foo `1` + `2` bar')

    def test___repr__(self):
        self.assertEqual(repr(self.p0),
                '<Possibility root="1 + 2" handler=dummy_handler args=(1, 2)>')

    def test___eq__(self):
        assert self.p0 == P(self.n, dummy_handler, (self.l1, self.l2))
        assert self.p0 != self.p1

    def test_multiple_input(self):
        parser = ParserWrapper(Parser)
        parser.run(['1+2', '?', '3+4', '?'])
        possibilities = parser.parser.possibilities
        self.assertEqual('\n'.join([repr(pos) for pos in possibilities]),
                    '<Possibility root="3 + 4" handler=add_numerics' \
                    ' args=(<Scope of "3 + 4">, 3, 4)>')

    def test_multiple_runs(self):
        parser = ParserWrapper(Parser)
        parser.run(['1+2', '?'])
        possibilities = parser.parser.possibilities
        self.assertEqual('\n'.join([repr(pos) for pos in possibilities]),
                    '<Possibility root="1 + 2" handler=add_numerics' \
                    ' args=(<Scope of "1 + 2">, 1, 2)>')

        # Remove previous possibilities after second run() call.
        parser.run(['', ' '])
        possibilities = parser.parser.possibilities
        self.assertEqual(possibilities, None)

        # Overwrite previous possibilities with new ones
        parser.run(['3+4', '?'])
        possibilities = parser.parser.possibilities
        self.assertEqual('\n'.join([repr(pos) for pos in possibilities]),
                    '<Possibility root="3 + 4" handler=add_numerics' \
                    ' args=(<Scope of "3 + 4">, 3, 4)>')

    def test_flatten_mult(self):
        self.assertEqual(flatten_mult(tree('2(xx)')), tree('2xx'))
        self.assertEqual(flatten_mult(tree('2(xx) + 1')), tree('2xx + 1'))
