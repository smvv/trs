import unittest

from src.possibilities import MESSAGES, Possibility as P, filter_duplicates
from tests.test_rules_poly import tree


def dummy_handler(root, args):
    return root


def dummy_handler_msg(root, args):
    return root


MESSAGES[dummy_handler_msg] = 'foo {1} + {2} bar'


class TestPossibilities(unittest.TestCase):

    def setUp(self):
        self.l1, self.l2 = self.n = tree('1 + 2')
        self.p0 = P(self.n, dummy_handler, (self.l1, self.l2))
        self.p1 = P(self.n, dummy_handler_msg, (self.l1, self.l2))

    def test___str__(self):
        self.assertEqual(str(self.p0),
                '<Possibility root="1 + 2" handler=dummy_handler args=(1, 2)>')
        self.assertEqual(str(self.p1), 'foo 1 + 2 bar')

    def test___repr__(self):
        self.assertEqual(repr(self.p0),
                '<Possibility root="1 + 2" handler=dummy_handler args=(1, 2)>')

    def test___eq__(self):
        assert self.p0 == P(self.n, dummy_handler, (self.l1, self.l2))
        assert self.p0 != self.p1

    def test_filter_duplicates(self):
        self.assertEqual(filter_duplicates([]), [])
        self.assertEqual(filter_duplicates([1, 2]), [1, 2])
        self.assertEqual(filter_duplicates([1, 2, 2]), [1, 2])
        self.assertEqual(filter_duplicates([1, 2, 3, 2]), [1, 2, 3])
