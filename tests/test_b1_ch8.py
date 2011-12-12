import unittest

from src.parser import Parser
from src.node import ExpressionNode as N, ExpressionLeaf as L
from tests.parser import run_expressions


class TestB1Ch8(unittest.TestCase):

    def test_diagnostic_test(self):
        run_expressions(Parser, [
            ('6*5^2', N('*', L(6), N('^', L(5), L(2)))),
            ('-5*(-3)^2', N('*', N('-', L(5)),
                                 N('^', N('-', L(3)), L(2)))),
            ('-5*(-3)^2', N('*', N('-', L(5)),
                                 N('^', N('-', L(3)), L(2)))),
            ('7p-3p', N('-', N('*', L(7), L('p')), N('*', L(3), L('p')))),
            ('-5a*-6', N('*', N('-', L(5)), L('a'), N('-', L(6)))),
            ('3a-8--5-2a', N('-', N('*', L(3), L('a')), L(8),
                                  N('-', L(5)), N('*', L(2), L('a')))),
            ])
