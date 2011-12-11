import unittest

from src.parser import Parser
from src.node import ExpressionNode as N, ExpressionLeaf as L
from tests.parser import ParserWrapper, run_expressions


class TestCalc(unittest.TestCase):

    def test_constructor(self):
        assert ParserWrapper(Parser).run(['1+4']) \
                == N('+', L(1), L(4))

    def test_basic_on_exp(self):
        expressions = [('4',   L(4)),
                       ('3+4', N('+', L(3), L(4))),
                       ('3-4', N('-', L(3), L(4))),
                       ('3/4', N('/', L(3), L(4))),
                       ('-4',  N('-', L(4))),
                       ('3^4', N('^', L(3), L(4))),
                       ('(2)', L(2))]

        run_expressions(Parser, expressions)

    def test_infinity(self):
        expressions = [('2^3000',  N('^', L(2), L(3000))),
                       ('2^-3000', N('^', L(2), N('-', L(3000))))]
        #               ('2^99999999999', None),
        #               ('2^-99999999999', 0.0)]

        run_expressions(Parser, expressions)

    def test_concat_easy(self):
        expressions = [
                       ('xy',     N('*', L('x'), L('y'))),
                       ('2x',     N('*', L(2), L('x'))),
                       ('x4',     N('^', L('x'), L(4))),
                       ('3 4',    N('*', L(3), L(4))),
                       ('xy4',    N('*', L('x'), N('^', L('y'), L(4)))),
                       ('(x)4',   N('*', L('x'), L(4))),
                       ('(3+4)2', N('*', N('+', L(3), L(4)), L(2))),
                      ]

        run_expressions(Parser, expressions)

    def test_concat_intermediate(self):
        expressions = [
                       ('(3+4)(5+7)', N('*', N('+', L(3), L(4)),
                                             N('+', L(5), L(7)))),
                       ('(a+b)(c+d)', N('*', N('+', L('a'), L('b')),
                                             N('+', L('c'), L('d')))),
                       ('a+b(c+d)',   N('+', L('a'), N('*', L('b'),
                                             N('+', L('c'), L('d'))))),
                       ('abcd',   N('*', L('a'), L('b'), L('c'), L('d'))),
                       ('ab(c)d',   N('*', L('a'), L('b'), L('c'), L('d'))),
                       #('ab(c)d',   N('*', L('a'), N('*', L('b'),
                       #                              N('*', L('c'), L('d'))))),
                       ('ab*(c)*d',   N('*', L('a'), L('b'), L('c'), L('d'))),
                       ('ab*(c)^d',   N('*', L('a'), L('b'),
                                        N('^', L('c'), L('d')))),
                      ]

        run_expressions(Parser, expressions)

    def test_pow_nested(self):
        # a^b^c = a^(b^c) != (a^b)^c

        a, b, c, d, e = L('a'), L('b'), L('c'), L('d'), L('e')

        expressions = [
                       ('a^b^c', N('^', a, N('^', b, c))),
                       ('-1^b^c', N('-', N('^', L(1), N('^', b, c)))),
                       ('ab^c', N('*', a, N('^', b, c))),
                       ('a(b)^c', N('*', a, N('^', b, c))),
                       ('a(b+c)^(d+e)', N('*', a, N('^', N('+', b, c),
                                                  N('+', d, e)))),
                       ('(a(b+c))^(d+e)', N('^', N('*', a, N('+', b, c)),
                                            N('+', d, e))),
                      ]

        run_expressions(Parser, expressions)
