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
from itertools import permutations

from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_ADD, OP_MUL, \
        OP_DIV, OP_SIN, OP_COS, OP_TAN, OP_SQRT, PI, TYPE_OPERATOR, sin, cos, \
        Scope, negate
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_quadrants(node):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)

    for sin_q, cos_q in permutations(scope, 2):
        if sin_q.is_power(2) and cos_q.is_power(2):
            s, c = sin_q[0], cos_q[0]

            if not s.is_op(OP_SIN) or not c.is_op(OP_COS) or s.negated \
                    or c.negated or s[0] != c[0]:
                continue

            if not sin_q.negated and not cos_q.negated:
                p.append(P(node, add_quadrants, (scope, sin_q, cos_q)))
            elif sin_q.negated == 1 and cos_q.negated == 1:
                p.append(P(node, factor_out_quadrant_negation,
                    (scope, sin_q, cos_q)))

    return p


def add_quadrants(root, args):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    scope, s, c = args
    scope.replace(s, L(1))
    scope.remove(c)

    return scope.as_nary_node()


MESSAGES[add_quadrants] = _('Add the sinus and cosinus quadrants to `1`.')


def factor_out_quadrant_negation(root, args):
    """
    -sin(t) ^ 2 - cos(t) ^ 2  ->  -(sin(t) ^ 2 + cos(t) ^ 2)  # ->  -1
    """
    scope, s, c = args
    scope.replace(s, -(+s + +c))
    scope.remove(c)

    return scope.as_nary_node()


MESSAGES[factor_out_quadrant_negation] = _('Factor out the negations of {2} ' \
        'and {3} to be able to reduce the quadrant addition to `1`.')


def match_negated_parameter(node):
    """
    sin(-t)  ->  -sin(t)
    cos(-t)  ->  cos(t)
    """
    assert node.is_op(OP_SIN) or node.is_op(OP_COS)

    t = node[0]

    if t.negated:
        if node.op == OP_SIN:
            return [P(node, negated_sinus_parameter, (t,))]

        return [P(node, negated_cosinus_parameter, (t,))]

    return []


def negated_sinus_parameter(root, args):
    """
    sin(-t)  ->  -sin(t)
    """
    return negate(sin(+args[0]), root.negated + 1)


MESSAGES[negated_sinus_parameter] = \
        _('Bring the negation from the sinus parameter {1} to the outside.')


def negated_cosinus_parameter(root, args):
    """
    cos(-t)  ->  cos(t)
    """
    return cos(+args[0])


MESSAGES[negated_cosinus_parameter] = \
        _('Remove the negation from the cosinus parameter {1}.')


def match_half_pi_subtraction(node):
    """
    sin(pi / 2 - t)  ->  cos(t)
    cos(pi / 2 - t)  ->  sin(t)
    """
    assert node.is_op(OP_SIN) or node.is_op(OP_COS)

    if node[0].is_op(OP_ADD):
        half_pi, t = node[0]

        if half_pi == L(PI) / 2:
            if node.op == OP_SIN:
                return [P(node, half_pi_subtraction_sinus, (t,))]

    return []


def half_pi_subtraction_sinus(root, args):
    pass


def is_pi_frac(node, denominator):
    """
    Check if a node is a fraction of 1 multiplied with PI.

    Example:
    >>> print is_pi_frac(L(1) / 2 * L(PI), 2)
    True
    """
    if not node.is_op(OP_MUL):
        return False

    frac, pi = node

    if not frac.is_op(OP_DIV) or not pi.is_leaf or pi.value != PI:
        return False

    n, d = frac

    return n == 1 and d == denominator


def sqrt(value):
    return N(OP_SQRT, L(value))


l0, l1, sq2, sq3 = L(0), L(1), sqrt(2), sqrt(3)
half = l1 / 2

CONSTANTS = {
    OP_SIN: [l0, half, half * sq2, half * sq3, l1, l0],
    OP_COS: [l1, half * sq3, half * sq2, half, l0, -l1],
    OP_TAN: [l0, l1 / 3 * sq3, l1, sq3, l0]
}


def match_standard_radian(node):
    """
    Apply a direct constant calculation from the constants table:

        | 0 | pi / 6    | pi / 4    | pi / 3    | pi / 2 | pi
    ----+---+-----------+-----------+-----------+--------+---
    sin | 0 | 1/2       | sqrt(2)/2 | sqrt(3)/2 | 1      | 0
    cos | 1 | sqrt(3)/2 | sqrt(2)/2 | 1/2       | 0      | -1
    tan | 0 | sqrt(3)/3 | 1         | sqrt(3)   | -      | 0
    """
    assert node.type == TYPE_OPERATOR and node.op in (OP_SIN, OP_COS, OP_TAN)

    t = node[0]

    if t == 0:
        return [P(node, standard_radian, (node.op, 0))]

    if t == PI:
        return [P(node, standard_radian, (node.op, 5))]

    denoms = [6, 4, 3]

    if node.op != OP_TAN:
        denoms.append(2)

    for i, denominator in enumerate(denoms):
        if is_pi_frac(t, denominator):
            return [P(node, standard_radian, (node.op, i + 1))]

    return []


def standard_radian(root, args):
    op, column = args

    return CONSTANTS[op][column].negate(root.negated)


MESSAGES[standard_radian] = _('Replace standard radian {0}.')
