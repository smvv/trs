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
from parser import Parser
from possibilities import apply_suggestion
from strategy import find_possibilities
from tests.parser import ParserWrapper


VALIDATE_FAILURE = 0
VALIDATE_NOPROGRESS = 1
VALIDATE_SUCCESS = 2
VALIDATE_ERROR = 3


def validate(a, b):
    """
    Validate that a =>* b.
    """
    parser = ParserWrapper(Parser)

    # Parse both expressions
    a = parser.run([a])
    b = parser.run([b])

    # Evaluate a and b, counting the number of steps
    # TODO: Optimization: if b is encountered while evaluating a, return
    # VALIDATION_SUCCESS
    parser.set_root_node(a)
    A, a_steps = parser.rewrite_and_count_all()

    if not a:
        return VALIDATE_ERROR

    parser.set_root_node(b)
    B, b_steps = parser.rewrite_and_count_all()

    if not B:
        return VALIDATE_ERROR

    # Evaluations must be equal
    if not A.equals(B):
        return VALIDATE_FAILURE

    # If evaluation of b took more staps than evaluation of a, the step from a
    # to b was probably useless or even bad
    if b_steps >= a_steps:
        return VALIDATE_NOPROGRESS

    # Evaluations match and b is evaluated quicker than a => success
    return VALIDATE_SUCCESS
