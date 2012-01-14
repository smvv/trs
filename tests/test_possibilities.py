import unittest

from src.possibilities import MESSAGES, Possibility as P, filter_duplicates
from src.rules.numerics import add_numerics
from tests.test_rules_poly import tree


def dummy_handler(root, args):  # pragma: nocover
    pass


def dummy_handler_msg(root, args):  # pragma: nocover
    pass


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
        a, b = ab = tree('a + b')
        p0 = P(a, dummy_handler, (1, 2))
        p1 = P(ab, dummy_handler, (1, 2))
        p2 = P(ab, dummy_handler, (1, 2, 3))
        p3 = P(ab, dummy_handler_msg, (1, 2))

        self.assertEqual(filter_duplicates([]), [])
        self.assertEqual(filter_duplicates([p0, p1]), [p1])
        self.assertEqual(filter_duplicates([p1, p2]), [p1, p2])
        self.assertEqual(filter_duplicates([p1, p3]), [p1, p3])
        self.assertEqual(filter_duplicates([p0, p1, p2, p3]), [p1, p2, p3])

        # Docstrings example
        (l1, l2), l3 = left, l3 = right = tree('1 + 2 + 3')
        p0 = P(left, add_numerics, (1, 2, 1, 2))
        p1 = P(right, add_numerics, (1, 2, 1, 2))
        p2 = P(right, add_numerics, (1, 3, 1, 3))
        p3 = P(right, add_numerics, (2, 3, 2, 3))
        self.assertEqual(filter_duplicates([p0, p1, p2, p3]), [p1, p2, p3])
