# vim: set fileencoding=utf-8 :
import unittest

from src.parser import Parser
from tests.parser import ParserWrapper


class TestException(unittest.TestCase):
    def test_raise(self):
        try:
            ParserWrapper(Parser).run(['raise'])
        except RuntimeError:
            return

        raise AssertionError('Expected raised RuntimeError!') # pragma: nocover
