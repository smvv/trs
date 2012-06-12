# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
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

    #def test_success(self):
    #    self.assertTrue(validate('x^2 + x - 2x^2 + 3x + 1',
    #                             'x^2 + 4x - 2x^2 + 1'))

    #def test_indefinite_integral(self):
    #    self.assertTrue(validate('int_2^4 x^2', '4^3/3 - 2^3/3'))

    #def test_advanced_failure(self):
    #    self.assertFalse(validate('(x-1)^3+(x-1)^3', '4a+4b'))

    def test_sphere_volume(self):
        self.assertTrue(validate('int_(-r)^(r) pi * (r^2 - x^2) dx',
                                 '4 / 3 * pi * r ^ 3'))
