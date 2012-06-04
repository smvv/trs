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
from ..node import Scope, OP_ADD, OP_MUL, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_negated_factor(node):
    """
    This rule assures that negations in the scope of a multiplication are
    brought to the multiplication itself.

    Examples:
    (-a)b   ->  -ab
    a * -b  ->  -ab
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)

    for factor in scope:
        if factor.negated:
            p.append(P(node, negated_factor, (scope, factor)))

    return p


def negated_factor(root, args):
    """
    (-a)b   ->  -ab
    a * -b  ->  -ab
    """
    scope, factor = args
    scope.replace(factor, +factor)

    return -scope.as_nary_node()


MESSAGES[negated_factor] = \
        _('Bring negation of {2} to the outside of the multiplication.')


def match_negate_polynome(node):
    """
    --a       ->  a
    ----a     ->  --a
    -(a + b)  ->  -a - b
    -0        ->  0
    """
    assert node.negated, str(node.negated) + '; ' + str(node)

    p = []

    if not (node.negated & 1):
        # --a, ----a
        p.append(P(node, double_negation))

    if node == 0 or node == 0.0:
        # -0
        p.append(P(node, negated_zero))
    elif node.is_op(OP_ADD):
        # -(a + b)  ->  -a - b
        p.append(P(node, negate_polynome))

    return p


def double_negation(root, args):
    """
    --a    ->  a
    ----a  ->  --a
    ...
    """
    return root.reduce_negation(2)


MESSAGES[double_negation] = _('Remove double negation in {0}.')


def negated_zero(root, args):
    """
    -0  ->  0
    """
    return root.reduce_negation()


MESSAGES[negated_zero] = _('Remove negation from zero.')


def negate_polynome(root, args):
    """
    -(a + b)  ->  -a - b
    """
    scope = Scope(root)

    # Negate each group
    for i, n in enumerate(scope):
        scope[i] = -n

    return +scope.as_nary_node()


MESSAGES[negate_polynome] = _('Apply negation to the polynome {0}.')


def match_negated_division(node):
    """
    (-a) / b  ->  -a / b
    a / (-b)  ->  -a / b

    Note that:
    (-a) / (-b)  ->  -a / (-b)  ->  --a / b  ->  a / b
    """
    assert node.is_op(OP_DIV)

    a, b = node
    p = []

    if a.negated:
        p.append(P(node, negated_nominator))

    if b.negated:
        p.append(P(node, negated_denominator))

    return p


def negated_nominator(root, args):
    """
    (-a) / b  ->  -a / b
    """
    a, b = root

    return -(+a / b).negate(root.negated)


MESSAGES[negated_nominator] = \
        _('Bring nominator negation in {0} outside to the fraction itself.')


def negated_denominator(root, args):
    """
    a / (-b)  ->  -a / b
    """
    a, b = root

    return -(a / +b).negate(root.negated)


MESSAGES[negated_denominator] = \
        _('Bring denominator negation in {0} outside to the fraction itself.')
