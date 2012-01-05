import unittest

from src.node import ExpressionNode as N, ExpressionLeaf as L


class TestNode(unittest.TestCase):

    def setUp(self):
        self.l = [L(1), N('*', L(2), L(3)), L(4), L(5)]

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

    def test_extract_polynome_properties_identifier(self):
        self.assertEqual(L('a').extract_polynome_properties(),
                         (L(1), L('a'), L(1)))

    def test_extract_polynome_properties_None(self):
        self.assertIsNone(N('+').extract_polynome_properties())

    def test_extract_polynome_properties_power(self):
        power = N('^', L('a'), L(2))
        self.assertEqual(power.extract_polynome_properties(),
                         (L(1), L('a'), L(2)))

    def test_extract_polynome_properties_coefficient_exponent_int(self):
        times = N('*', L(3), N('^', L('a'), L(2)))
        self.assertEqual(times.extract_polynome_properties(),
                         (L(3), L('a'), L(2)))

    def test_extract_polynome_properties_coefficient_exponent_id(self):
        times = N('*', L(3), N('^', L('a'), L('b')))
        self.assertEqual(times.extract_polynome_properties(),
                         (L(3), L('a'), L('b')))

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
