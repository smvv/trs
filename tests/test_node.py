import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L


class TestNode(unittest.TestCase):

    def setUp(self):
        self.l = [L(1), N('*', L(2), L(3)), L(4), L(5)]

    def test_replace_node(self):
        inner = N('+', L(1), L(2))
        node = N('+', inner, L(3))
        replacement = N('-', L(4), L(5))
        inner.replace(replacement)
        self.assertEqual(str(node), '4 - 5 + 3')

    def test_replace_leaf(self):
        inner = N('+', L(1), L(2))
        node = N('+', inner, L(3))
        replacement = L(4)
        inner.replace(replacement)
        self.assertEqual(str(node), '4 + 3')

    def test_is_power_true(self):
        self.assertTrue(N('^', *self.l[:2]).is_power())
        self.assertFalse(N('+', *self.l[:2]).is_power())

    def test_is_nary(self):
        self.assertTrue(N('+', *self.l[:2]).is_nary())
        self.assertTrue(N('-', *self.l[:2]).is_nary())
        self.assertTrue(N('*', *self.l[:2]).is_nary())
        self.assertFalse(N('^', *self.l[:2]).is_nary())

    def test_is_identifier(self):
        self.assertTrue(L('a').is_identifier())
        self.assertFalse(L(1).is_identifier())

    def test_is_int(self):
        self.assertTrue(L(1).is_int())
        self.assertFalse(L(1.5).is_int())
        self.assertFalse(L('a').is_int())

    def test_is_float(self):
        self.assertTrue(L(1.5).is_float())
        self.assertFalse(L(1).is_float())
        self.assertFalse(L('a').is_float())

    def test_is_numeric(self):
        self.assertTrue(L(1).is_numeric())
        self.assertTrue(L(1.5).is_numeric())
        self.assertFalse(L('a').is_numeric())

    def test_get_order_identifier(self):
        self.assertEqual(L('a').get_order(), ('a', 1, 1))

    def test_get_order_None(self):
        self.assertIsNone(L(1).get_order())

    def test_get_order_power(self):
        power = N('^', L('a'), L(2))
        self.assertEqual(power.get_order(), ('a', 2, 1))

    def test_get_order_coefficient_exponent_int(self):
        times = N('*', L(3), N('^', L('a'), L(2)))
        self.assertEqual(times.get_order(), ('a', 2, 3))

    def test_get_order_coefficient_exponent_id(self):
        times = N('*', L(3), N('^', L('a'), L('b')))
        self.assertEqual(times.get_order(), ('a', 'b', 3))

    def test_get_scope_binary(self):
        plus = N('+', *self.l[:2])
        self.assertEqual(plus.get_scope(), self.l[:2])

    def test_get_scope_nested_left(self):
        plus = N('+', N('+', *self.l[:2]), self.l[2])
        self.assertEqual(plus.get_scope(), self.l[:3])

    def test_get_scope_nested_right(self):
        plus = N('+', self.l[0], N('+', *self.l[1:3]))
        self.assertEqual(plus.get_scope(), self.l[:3])

    def test_get_scope_nested_deep(self):
        plus = N('+', N('+', N('+', *self.l[:2]), self.l[2]), self.l[3])
        self.assertEqual(plus.get_scope(), self.l)
