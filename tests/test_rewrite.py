from unittest import TestCase

from src.parser import Parser
from tests.parser import ParserWrapper


def rewrite(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp, '@'])


class TestRewrite(TestCase):

    def assertRewrite(self, rewrite_chain):
        try:
            for i, exp in enumerate(rewrite_chain[:-1]):
                self.assertEqual(str(rewrite(exp)), str(rewrite_chain[i+1]))
        except AssertionError:  # pragma: nocover
            print 'rewrite failed:', exp, '->', rewrite_chain[i+1]
            print 'rewrite chain:', rewrite_chain
            raise

    def test_addition_rewrite(self):
        self.assertRewrite(['2 + 3 + 4', '5 + 4', '9'])

    def test_addition_identifiers_rewrite(self):
        self.assertRewrite(['2 + 3a + 4', '6 + 3a'])

    def test_division_rewrite(self):
        self.assertRewrite(['2/7 - 4/11', '22 / 77 + -28 / 77',
                            '(22 + -28) / 77', '-6 / 77'])
