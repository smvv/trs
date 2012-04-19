from unittest import TestCase
from src.validation import validate


class TestValidation(TestCase):

    def test_simple_success(self):
        self.assertTrue(validate('3a + a', '4a'))

    def test_simple_failure(self):
        self.assertFalse(validate('3a + a', '4a + 1'))

    def test_intermediate_success(self):
        self.assertTrue(validate('3a + a + b + 2b', '4a + 3b'))
        self.assertTrue(validate('a / b / (c / d)', '(ad) / (bc)'))

    def test_intermediate_failure(self):
        self.assertFalse(validate('3a + a + b + 2b', '4a + 4b'))

    #def test_indefinite_integral(self):
    #    self.assertTrue(validate('int_2^4 x^2', '4^3/3 - 2^3/3'))

    #def test_advanced_failure(self):
    #    self.assertFalse(validate('(x-1)^3+(x-1)^3', '4a+4b'))
