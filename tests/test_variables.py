import unittest

from src.calc import Parser
from tests.parser import run_expressions
from sympy import Symbol, symbols


class TestVariables(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_addition(self):
        expressions = [('5 + 5', 5 + 5)]
        run_expressions(Parser, expressions)

    def test_addition_of_one_term(self):
        a = Symbol('a')
        expressions = [('a + 5', 5 + a)]
        run_expressions(Parser, expressions)

    def test_addition_of_two_terms(self):
        a, b = symbols('a,b')
        expressions = [('4*a + 5*b', 4*a + 5*b)]
        run_expressions(Parser, expressions)

    #def test_short_addition_of_two_terms(self):
    #    a, b = symbols('a,b')
    #    expressions = [('4a + 5b', 4.0*a + 5.0*b)]
    #    run_expressions(expressions, verbose=1)
