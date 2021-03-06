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
from itertools import combinations

from .utils import greatest_common_divisor, is_numeric_node
from ..node import ExpressionLeaf as Leaf, Scope, OP_ADD, OP_DIV, OP_MUL, \
        OP_POW
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_numerics(node):
    """
    Combine two constants to a single constant in an n-ary addition.

    Example:
    2 + 3    ->  5
    2 + -3   ->  -1
    -2 + 3   ->  1
    -2 + -3  ->  -5
    0 + 3    ->  3
    0 + -3   ->  -3
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)
    numerics = []

    for n in scope:
        if n == 0:
            p.append(P(node, remove_zero, (scope, n)))
        elif n.is_numeric():
            numerics.append(n)

    for c0, c1 in combinations(numerics, 2):
        p.append(P(node, add_numerics, (scope, c0, c1)))

    return p


def remove_zero(root, args):
    """
    0 + a  ->  a
    """
    scope, n = args
    scope.remove(n)

    return scope.as_nary_node()


MESSAGES[remove_zero] = _('Remove addition of zero.')


def add_numerics(root, args):
    """
    2 + 3    ->  5
    2 + -3   ->  -1
    -2 + 3   ->  1
    -2 + -3  ->  -5
    """
    scope, c0, c1 = args
    scope.replace(c0, Leaf(c0.actual_value() + c1.actual_value()))
    scope.remove(c1)

    return scope.as_nary_node()


MESSAGES[add_numerics] = _('Add the constants {2} and {3}.')


def match_divide_numerics(node):
    """
    Combine two constants to a single constant in a division, if it does not
    lead to a decrease in precision.

    Example:
    6 / 2      ->  3
    3 / 2      ->  3 / 2      # 1.5 would mean a decrease in precision
    3.0 / 2    ->  1.5
    3 / 2.0    ->  1.5
    3.0 / 2.0  ->  1.5
    3 / 1.0    ->  3          # Exceptional case: division of integer by 1.0
                              # keeps integer precision
    2 / 4      ->  1 / 2      # 1 < greatest common divisor <= nominator
    4 / 3      ->  1 + 1 / 3  # nominator > denominator
    """
    assert node.is_op(OP_DIV)

    n, d = node

    if n.negated or d.negated:
        return []

    nv, dv = n.value, d.value

    if n.is_int() and d.is_int():
        mod = nv % dv

        if not mod:
            # 6 / 2  ->  3
            # 3 / 2  ->  3 / 2
            return [P(node, divide_numerics)]

        gcd = greatest_common_divisor(nv, dv)

        if 1 < gcd <= nv:
            # 2 / 4  ->  1 / 2
            return [P(node, reduce_fraction_constants, (gcd,))]

        #if nv > dv:
        #    # 4 / 3  ->  1 + 1 / 3
        #    return [P(node, fraction_to_int_fraction,
        #              ((nv - mod) / dv, mod, dv))]
    elif n.is_numeric() and d.is_numeric():
        if d == 1.0:
            # 3 / 1.0  ->  3
            dv = 1

        # 3.0 / 2  ->  1.5
        # 3 / 2.0  ->  1.5
        # 3.0 / 2.0  ->  1.5
        return [P(node, divide_numerics)]

    return []


def divide_numerics(root, args):
    """
    Combine two divided constants into a single constant.

    Examples:
    6 / 2      ->  3
    3.0 / 2    ->  1.5
    3 / 2.0    ->  1.5
    3.0 / 2.0  ->  1.5
    3 / 1.0    ->  3
    """
    n, d = root

    return Leaf(n.value / d.value, negated=root.negated)


MESSAGES[divide_numerics] = _('Constant division {0} reduces to a number.')


def reduce_fraction_constants(root, args):
    """
    Reduce the nominator and denominator of a fraction with a given greatest
    common divisor.

    Example:
    2 / 4  ->  1 / 2
    """
    gcd = args[0]
    a, b = root

    return Leaf(a.value / gcd) / Leaf(b.value / gcd)


MESSAGES[reduce_fraction_constants] = \
        _('Divide the nominator and denominator of fraction {0} by {1}.')


def match_multiply_numerics(node):
    """
    3 * 2      ->  6
    3.0 * 2    ->  6.0
    3 * 2.0    ->  6.0
    3.0 * 2.0  ->  6.0
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)
    numerics = filter(is_numeric_node, scope)

    for n in numerics:
        if n.value == 0:
            p.append(P(node, multiply_zero, (n,)))

        if not n.negated and n.value == 1:
            p.append(P(node, multiply_one, (scope, n)))

    for c0, c1 in combinations(numerics, 2):
        p.append(P(node, multiply_numerics, (scope, c0, c1)))

    return p


def multiply_zero(root, args):
    """
    0 * a   ->  0
    -0 * a  ->  -0
    """
    return args[0].negate(root.negated)


MESSAGES[multiply_zero] = _('Multiplication with zero yields zero.')


def multiply_one(root, args):
    """
    1 * a   ->  a
    -1 * a  ->  -a
    """
    scope, one = args
    scope.remove(one)

    return scope.as_nary_node().negate(one.negated)


MESSAGES[multiply_one] = _('Multiplication with one yields the multiplicant.')


def multiply_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary multiplication.

    Example:
    2 * 3  ->  6
    """
    scope, c0, c1 = args

    # Replace the left node with the new expression
    substitution = Leaf(c0.value * c1.value, negated=c0.negated + c1.negated)
    scope.replace(c0, substitution)

    # Remove the right node
    scope.remove(c1)

    return scope.as_nary_node()


MESSAGES[multiply_numerics] = _('Multiply constant {2} with {3}.')


def match_raise_numerics(node):
    """
    2 ^ 3     ->  8
    (-2) ^ 3  ->  -8
    (-2) ^ 2  ->  4
    """
    assert node.is_op(OP_POW)

    r, e = node

    if r.is_numeric() and e.is_numeric() and not e.negated:
        return [P(node, raise_numerics, (r, e, node.negated))]

    return []


def raise_numerics(root, args):
    """
    2 ^ 3     ->  8
    (-2) ^ 3  ->  -8
    (-2) ^ 2  ->  4
    """
    r, e, negated = args

    return Leaf(r.value ** e.value, negated=r.negated * e.value + negated)


MESSAGES[raise_numerics] = _('Raise constant {1} with {2}.')
