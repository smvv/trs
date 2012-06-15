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

from src.parser import Parser
from src.node import ExpressionNode as N, ExpressionLeaf as L
from tests.parser import run_expressions


class TestB1Ch10(unittest.TestCase):

    def test_diagnostic_test(self):
        run_expressions(Parser, [
            ('5(a-2b)', L(5) * (L('a') + -(L(2) * 'b'))),
            ('-(3a+6b)', -(L(3) * L('a') + L(6) * 'b')),
            ('18-(a-12)', L(18) + -(L('a') + -L(12))),
            ('-p-q+5(p-q)-3q-2(p-q)',
                -L('p') + -L('q') + L(5) * (L('p') + -L('q')) + -(L(3) * 'q') \
                + -(L(2) * (L('p') + -L('q')))
            ),
            ('(2+3/7)^4',
                N('^', N('+', L(2), N('/', L(3), L(7))), L(4))
            ),
            ('x^3*x^2*x',
                N('*',
                  N('*',
                    N('^', L('x'), L(3)),
                    N('^', L('x'), L(2))),
                  L('x')
                )
            ),
            ('-x^3*-2x^5',
                -(L('x') ** L(3) * -L(2) * L('x') ** L(5))
            ),
            ('(7x^2y^3)^2/(7x^2y^3)',
                N('/',
                  N('^',
                    N('*',
                      N('*', L(7), N('^', L('x'), L(2))),
                      N('^', L('y'), L(3))
                    ),
                    L(2)),
                  N('*',
                    N('*', L(7), N('^', L('x'), L(2))),
                    N('^', L('y'), L(3))
                  )
                )
            ),
            ])
