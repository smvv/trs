from unittest import TestCase

from src.parser import Parser
from tests.parser import ParserWrapper


def rewrite(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp, '@'])


class TestLeidenOefenopgave(TestCase):
    def test_1(self):
        return
        for exp, solution in [
                ('-5(x2 -3x + 6)',       '-30 + 15 * x - 5 * x ^ 2'),
                ('(x+1)^2',              'x ^ 2 + 2 * x + 1'),
                ('(x-1)^2',              'x ^ 2 - 2 * x + 1'),
                ('(2x+x)*x',             '3 * x ^ 2'),
                ('-2(6x-4)^2*x',         '-72 * x^3 + 96 * x ^ 2 + 32 * x'),
                ('(4x + 5) * -(5 - 4x)', '16x^2 - 25'),
                ]:
            self.assertEqual(str(rewrite(exp)), solution)

    def test_2(self):
        pass

    def test_3(self):
        pass

    def test_4(self):
        for exp, solution in [
                ('2/15 + 1/4',      '8 / 60 + 15 / 60'),
                ('8/60 + 15/60',    '(8 + 15) / 60'),
                ('(8 + 15) / 60',   '23 / 60'),
                # FIXME: ('2/7 - 4/11',      '-6 / 77'),
                # FIXME: ('(7/3) * (3/5)',   '7 / 5'),
                # FIXME: ('(3/4) / (5/6)',   '9 / 10'),
                # FIXME: ('1/4 * 1/x',       '1 / (4x)'),
                # FIXME: ('(3/x^2) / (x/7)', '21 / x^3'),
                # FIXME: ('1/x + 2/(x+1)',   '(3x + 1) / (x * (x + 1))'),
                ]:
            self.assertEqual(str(rewrite(exp)), solution)
