import unittest

from tests.parser import TestParser, run_expressions


class TestCalc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        assert TestParser(keepfiles=1).run(['1+4']) == 5.0

    def test_basic_on_exp(self):
        expressions = [('4', 4.0),
                       ('3+4', 7.0),
                       ('3-4', -1.0),
                       ('3/4', .75),
                       ('-4', -4.0),
                       ('3^4', 81.0),
                       ('(4)', 4.0)]

        run_expressions(expressions)

    def test_infinity(self):
        expressions = [('2^3000', 2**3000),
                       ('2^-3000', 0.0)]
        #               ('2^99999999999', None),
        #               ('2^-99999999999', 0.0)]

        run_expressions(expressions)
