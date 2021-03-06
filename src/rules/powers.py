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

from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, \
                   OP_MUL, OP_DIV, OP_POW, OP_ADD, OP_SQRT, negate
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_exponents(node):
    """
    a^p * a^q  ->  a^(p + q)
    a * a^q    ->  a^(1 + q)
    a^p * a    ->  a^(p + 1)
    a * a      ->  a^(1 + 1)
    -a * a^q   ->  -a^(1 + q)
    """
    assert node.is_op(OP_MUL)

    p = []
    powers = {}
    scope = Scope(node)

    for n in scope:
        # Order powers by their roots, e.g. a^p and a^q are put in the same
        # list because of the mutual 'a'
        if n.is_identifier():
            s = negate(n, 0, clone=True)
            exponent = L(1)
        elif n.is_op(OP_POW):
            s, exponent = n
        else:  # pragma: nocover
            continue

        s_str = str(s)

        if s_str in powers:
            powers[s_str].append((n, exponent, s))
        else:
            powers[s_str] = [(n, exponent, s)]

    for root, occurrences in powers.iteritems():
        # If a root has multiple occurences, their exponents can be added to
        # create a single power with that root
        if len(occurrences) > 1:
            for (n0, e1, a0), (n1, e2, a1) in combinations(occurrences, 2):
                p.append(P(node, add_exponents, (scope, n0, n1, a0, e1, e2)))

    return p


def add_exponents(root, args):
    """
    a^p * a^q  ->  a^(p + q)
    """
    scope, n0, n1, a, p, q = args

    # TODO: combine exponent negations

    # Replace the left node with the new expression
    scope.replace(n0, (a ** (p + q)).negate(n0.negated + n1.negated))

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[add_exponents] = _('Add the exponents of {2} and {3}.')


def match_subtract_exponents(node):
    """
    a^p / a^q  ->  a^(p - q)
    a^p / a    ->  a^(p - 1)
    a / a^q    ->  a^(1 - q)
    """
    assert node.is_op(OP_DIV)

    left, right = node
    left_pow, right_pow = left.is_op(OP_POW), right.is_op(OP_POW)

    if left_pow and right_pow and left[0] == right[0]:
        # A power is divided by a power with the same root
        return [P(node, subtract_exponents, tuple(left) + (right[1],))]

    if left_pow and left[0] == right:
        # A power is divided by a its root
        return [P(node, subtract_exponents, tuple(left) + (1,))]

    if right_pow and left == right[0]:
        # An identifier is divided by a power of itself
        return [P(node, subtract_exponents, (left, 1, right[1]))]

    return []


def subtract_exponents(root, args):
    """
    a^p / a^q  ->  a^(p - q)
    """
    a, p, q = args

    return a ** (p - q)


MESSAGES[subtract_exponents] = _('Substract the exponents {2} and {3}.')


def match_multiply_exponents(node):
    """
    (a^p)^q  ->  a^(pq)
    """
    assert node.is_op(OP_POW)

    left, right = node

    if left.is_op(OP_POW):
        return [P(node, multiply_exponents, tuple(left) + (right,))]

    return []


def multiply_exponents(root, args):
    """
    (a^p)^q  ->  a^(pq)
    """
    a, p, q = args

    return a ** (p * q)


MESSAGES[multiply_exponents] = _('Multiply the exponents {2} and {3}.')


def match_duplicate_exponent(node):
    """
    (ab)^p  ->  a^p * b^p
    """
    assert node.is_op(OP_POW)

    root, exponent = node

    if root.is_op(OP_MUL):
        return [P(node, duplicate_exponent, (list(Scope(root)), exponent))]

    return []


def duplicate_exponent(root, args):
    """
    (ab)^p   ->  a^p * b^p
    (abc)^p  ->  a^p * b^p * c^p
    """
    ab, p = args
    result = ab[0] ** p

    for b in ab[1:]:
        result *= b ** p

    return result


MESSAGES[duplicate_exponent] = _('Duplicate the exponent {2}.')


def match_raised_fraction(node):
    """
    (a / b) ^ p  ->  a^p / b^p
    """
    assert node.is_op(OP_POW)

    root, exponent = node

    if root.is_op(OP_DIV):
        return [P(node, raised_fraction, (root, exponent))]

    return []


def raised_fraction(root, args):
    """
    (a / b) ^ p  ->  a^p / b^p
    """
    (a, b), p = args

    return a ** p / b ** p


MESSAGES[raised_fraction] = _('Apply the exponent {2} to the nominator and'
        ' denominator of fraction {1}.')


def match_remove_negative_child(node):
    """
    a ^ -p                           ->  1 / a ^ p
    (-a) ^ p and p is an odd number  ->  -a ^ p
    """
    assert node.is_op(OP_POW)

    a, p = node
    pos = []

    if p.negated:
        pos.append(P(node, remove_negative_exponent))

    if a.negated and p.is_int() and p.value & 1:
        pos.append(P(node, remove_negative_root))

    return pos


def remove_negative_exponent(root, args):
    """
    a ^ -p  ->  1 / a ^ p
    """
    a, p = root
    return L(1) / a ** p.reduce_negation()


MESSAGES[remove_negative_exponent] = \
        _('Replace negative exponent {0[1]} with a division by one.')


def remove_negative_root(root, args):
    """
    (-a) ^ p and p is an odd number  ->  -a ^ p
    """
    a, p = root
    return -(a.reduce_negation() ** p)


MESSAGES[remove_negative_root] = _('{0[1]} is an odd number, so apply the ' \
        'negation of {0[0]} to the power itself.')


def match_exponent_to_root(node):
    """
    a^(1 / 2)  ->  sqrt(a)
    a^(n / 2)  ->  sqrt(a^n)
    """
    assert node.is_op(OP_POW)

    left, right = node

    if right.is_op(OP_DIV) and right[1] == 2:
        return [P(node, exponent_to_root)]

    return []


def exponent_to_root(root, args):
    """
    a^(1 / 2)  ->  sqrt(a)
    a^(n / 2)  ->  sqrt(a^n)
    """
    a, (n, _) = root

    return N(OP_SQRT, a if n == 1 else a ** n)


MESSAGES[exponent_to_root] = \
        _('Rewrite power with exponent {0[1]} to a square root.')


def match_extend_exponent(node):
    """
    (a + ... + z)^n -> (a + ... + z)(a + ... + z)^(n - 1)  # 1 < n < 4

    n is maxed at 3 because otherwise evaluations may get out of hand, and high
    school expressions do not contain powers higher than 3
    """
    assert node.is_op(OP_POW)

    left, right = node

    if right.is_numeric() and 1 < right.actual_value() < 4:
        for n in Scope(node):
            if n.is_op(OP_ADD):
                return [P(node, extend_exponent,
                          (left, right, right.actual_value() - 1))]

    return []


def extend_exponent(root, args):
    """
    (a + ... + z)^n -> (a + ... + z)(a + ... + z)^(n - 1)  # n > 1
    """
    left, right, extended_exp = args

    if right.value > 2:
        return left * left ** L(extended_exp)

    return left * left


MESSAGES[extend_exponent] = _('Split exponent {2} to exponents `1` and {3}.')


def match_constant_exponent(node):
    """
    (a + ... + z)^n -> (a + ... + z)(a + ... + z)^(n - 1)  # n > 1
    """
    assert node.is_op(OP_POW)

    exponent = node[1]

    if exponent == 0:
        return [P(node, remove_power_of_zero, ())]

    if exponent == 1:
        return [P(node, remove_power_of_one, ())]

    return []


def remove_power_of_zero(root, args):
    """
    a ^ 0  ->  1
    """
    return L(1)


MESSAGES[remove_power_of_zero] = _('Power of zero {0} rewrites to `1`.')


def remove_power_of_one(root, args):
    """
    a ^ 1  ->  a
    """
    return root[0]


MESSAGES[remove_power_of_one] = _('Remove the power of one in {0}.')
