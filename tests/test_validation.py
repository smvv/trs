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
from rulestestcase import RulesTestCase
from src.validation import validate, VALIDATE_SUCCESS as OK, \
        VALIDATE_FAILURE as FAIL, VALIDATE_NOPROGRESS as NP


class TestValidation(RulesTestCase):

    def test_simple_success(self):
        self.assertValidateSuccess('3a + a', '4a')

    def test_simple_failure(self):
        self.assertValidateFailure('3a + a', '4a + 1')

    def test_intermediate_success(self):
        self.assertValidateSuccess('3a + a + b + 2b', '4a + 3b')
        self.assertValidateSuccess('a / b / (c / d)', '(ad) / (bc)')

    def test_intermediate_failure(self):
        self.assertValidateFailure('3a + a + b + 2b', '4a + 4b')

    def test_success(self):
        self.assertValidateSuccess('x^2 + x - 2x^2 + 3x + 1',
                                 'x^2 + 4x - 2x^2 + 1')

    def test_indefinite_integral(self):
        self.assertValidateSuccess('int_2^4 x^2', '4^3/3 - 2^3/3')

    def test_advanced_failure(self):
        self.assertValidateFailure('(x-1)^3+(x-1)^3', '4a+4b')

    def test_sphere_volume(self):
        self.assertValidateSuccess('int_(-r)^(r) pi * (r^2 - x^2) dx',
                                  '4 / 3 * pi * r ^ 3')

    def test_sphere_volume_alternative_notation(self):
        self.assertValidateSuccess('int_(-r)^(r) pi * (r^2 - x^2) dx',
                                 '4 * pi * r ^ 3 / 3')

    def test_noprogress_simple(self):
        self.assertValidateNoprogress('2 + 2', '3 + 1')
