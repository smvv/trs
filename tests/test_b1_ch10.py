import unittest

from src.parser import Parser
from src.node import ExpressionNode as N, ExpressionLeaf as L
from tests.parser import run_expressions


class TestB1Ch10(unittest.TestCase):

    def test_diagnostic_test(self):
        run_expressions(Parser, [
            ('5(a-2b)', N('*', L(5), N('-', L('a'),
                                       N('*', L(2), L('b'))))),
            ('-(3a+6b)', N('-', N('+', N('*', L(3), L('a')),
                                  N('*', L(6), L('b'))))),
            ('18-(a-12)', N('-', L(18),
                            N('-', L('a'), L(12)))),
            ('-p-q+5(p-q)-3q-2(p-q)',
                N('-',
                  N('-',
                    N('+', N('-', N('-', L('p')), L('q')),
                      N('*', L(5), N('-', L('p'), L('q')))),
                    N('*', L(3), L('q'))
                  ),
                  N('*', L(2), N('-', L('p'), L('q')))
                )
            ),
            ('(2+3/7)^4',
                N('^', N('+', L(2), N('/', L(3), L(7))), L(4))
            ),
            ('x3*x2*x',
                N('*',
                  N('*',
                    N('^', L('x'), L(3)),
                    N('^', L('x'), L(2))),
                  L('x')
                )
            ),
            ('-x3*-2x5',
                N('*',
                  N('*',
                    N('-', N('^', L('x'), L(3))),
                    N('-', L(2))),
                  N('^', L('x'), L(5))
                )
            ),
            ('(7x2y3)^2/(7x2y3)',
                N('*',
                  N('*',
                    N('-', N('^', L('x'), L(3))),
                    N('-', L(2))),
                  N('^', L('x'), L(5))
                )
            ),
            ])
