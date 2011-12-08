# vim: set fileencoding=utf-8 :
import unittest

from src.parser import Parser
from tests.parser import ParserWrapper, run_expressions


class TestException(unittest.TestCase):
    def test_raise(self):
        try:
            ParserWrapper(Parser).run(['raise'])
        except RuntimeError:
            return

        # pragma: nocover
        raise AssertionError('Expected a raised RuntimeError!')
