import unittest

from src.parser import Parser
from src.node import ExpressionLeaf as L
from tests.parser import run_expressions, apply_expressions


class TestB1Ch08(unittest.TestCase):

    def test_diagnostic_test_parser(self):
        run_expressions(Parser, [
            ('6*5^2', L(6) * L(5) ** 2),
            ('-5*(-3)^2', -(L(5) * (-L(3)) ** 2)),
            ('7p-3p', L(7) * 'p' + -(L(3) * 'p')),
            ('-5a*-6', -(L(5) * 'a' * -L(6))),
            ('3a-8--5-2a', L(3) * 'a' + -L(8) + --(L(5)) + -(L(2) * 'a')),
            ])

    def test_diagnostic_test_application(self):
        apply_expressions(Parser, [
            ('7p+2p', 1, (L(7) + 2) * 'p'),
            ('7p-3p', 1, (L(7) + -L(3)) * 'p'),
            ])
