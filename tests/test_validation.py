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
from src.validation import validate, VALIDATE_SUCCESS as OK, \
        VALIDATE_FAILURE as FAIL, VALIDATE_NOPROGRESS as NP


class TestValidation(TestCase):

    def test_simple_success(self):
        self.assertEqual(validate('3a + a', '4a'), OK)

    def test_simple_failure(self):
        self.assertEqual(validate('3a + a', '4a + 1'), FAIL)

    def test_intermediate_success(self):
        self.assertEqual(validate('3a + a + b + 2b', '4a + 3b'), OK)
        self.assertEqual(validate('a / b / (c / d)', '(ad) / (bc)'), OK)

    def test_intermediate_failure(self):
        self.assertEqual(validate('3a + a + b + 2b', '4a + 4b'), FAIL)

    def test_success(self):
        self.assertEqual(validate('x^2 + x - 2x^2 + 3x + 1',
                                 'x^2 + 4x - 2x^2 + 1'), OK)

    def test_indefinite_integral(self):
        self.assertEqual(validate('int_2^4 x^2', '4^3/3 - 2^3/3'), OK)

    def test_advanced_failure(self):
        self.assertEqual(validate('(x-1)^3+(x-1)^3', '4a+4b'), FAIL)

    def test_sphere_volume(self):
        self.assertEqual(validate('int_(-r)^(r) pi * (r^2 - x^2) dx',
                                  '4 / 3 * pi * r ^ 3'), OK)

    def test_sphere_volume_alternative_notation(self):
        self.assertEqual(validate('int_(-r)^(r) pi * (r^2 - x^2) dx',
                                 '4 * pi * r ^ 3 / 3'), OK)

    def test_noprogress_simple(self):
        self.assertEqual(validate('2 + 2', '3 + 1'), NP)
