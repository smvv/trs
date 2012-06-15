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
from itertools import product

from .utils import is_numeric_node
from ..node import ExpressionNode as N, Scope, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def is_expandable(node):
    """
    Check if a node is expandable. Only additions that consist of not only
    numerics can be expanded.
    """
    return node.is_op(OP_ADD) \
            and not all(map(is_numeric_node, Scope(node)))


def match_expand(node):
    """
    Expand multiplication of non-numeric additions.

    Examples:
    (a + b)(c + d)  ->  ac + ad + bc + bd
    (b + c)a        ->  ab + ac
    a(b + c)        ->  ab + ac
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)
    l = len(scope)

    for distance in range(1, l):
        for i, left in enumerate(scope[:-distance]):
            right = scope[i + distance]
            l_expandable = is_expandable(left)
            r_expandable = is_expandable(right)

            if l_expandable and r_expandable:
                p.append(P(node, expand_double, (scope, left, right)))
            elif l_expandable ^ r_expandable:
                p.append(P(node, expand_single, (scope, left, right)))

    return p


def expand(root, args):
    """
    a(b + c)        ->  ab + ac
    (a + b)c        ->  ac + bc
    (a + b)(c + d)  ->  ac + ad + bc + bd
    etc..
    """
    scope, left, right = args

    left_scope = Scope(left) if left.is_op(OP_ADD) else [left]
    right_scope = Scope(right) if right.is_op(OP_ADD) else [right]

    add_scope = [l * r for l, r in product(left_scope, right_scope)]
    add = Scope(N(OP_ADD, *add_scope)).as_nary_node()
    add.negated = left.negated + right.negated

    scope.replace(left, add)
    scope.remove(right)

    return scope.as_nary_node()


def expand_double(root, args):
    return expand(root, args)


MESSAGES[expand_double] = _('Expand ({2})({3}).')


def expand_single(root, args):
    return expand(root, args)


MESSAGES[expand_single] = _('Expand ({2})({3}).')
