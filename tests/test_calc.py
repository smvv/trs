import sys
import unittest


from src.calc import Parser


class TestParser(Parser):

    def __init__(self, input_buffer, **kwargs):
        Parser.__init__(self, **kwargs)

        self.input_buffer = []
        self.input_position = 0

        map(self.append, input_buffer)

    def append(self, input):
        self.input_buffer.append(input + '\n')

    def read(self, nbytes):
        buffer = ''

        try:
            buffer = self.input_buffer[self.input_position]
        except IndexError:
            return ''

        self.input_position += 1

        return buffer


class TestCalc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def run_expressions(self, expressions, fail=True):
        for exp, out in expressions:
            try:
                res = TestParser([exp], keepfiles=1).run()
                assert res == out
            except:
                print >>sys.stderr, 'error: %s = %s, but expected: %s' \
                                    % (exp, str(res), str(out))
                if fail:
                    raise

    def test_constructor(self):
        assert TestParser(['1+4'], keepfiles=1).run() == 5.0

    def test_basic_on_exp(self):
        expressions = [('4', 4.0),
                       ('3+4', 7.0),
                       ('3-4', -1.0),
                       ('3/4', .75),
                       ('-4', -4.0),
                       ('3^4', 81.0),
                       ('(4)', 4.0)]

        self.run_expressions(expressions)

    def test_infinity(self):
        expressions = [('2^9999', None),
                       ('2^-9999', 0.0),
                       ('2^99999999999', None),
                       ('2^-99999999999', 0.0)]

        self.run_expressions(expressions, fail=False)
