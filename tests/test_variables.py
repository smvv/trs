import unittest

from tests.parser import TestParser, run_expressions
from sympy import Symbol, symbols


class TestVariables(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_addition(self):
        a = Symbol('a')
        expressions = [('a + 5', a + 5)]
        run_expressions(expressions)

    def test_addition_of_two_terms(self):
        a, b = symbols('a,b')
        expressions = [('4*a + 5*b', 4*a + 5*b)]
        run_expressions(expressions)

    #def test_short_addition_of_two_terms(self):
    #    a, b = symbols('a,b')
    #    expressions = [('4a + 5b', 4.0*a + 5.0*b)]
    #    run_expressions(expressions, verbose=1)
