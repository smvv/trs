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
from itertools import permutations, combinations

from .utils import find_variable, evals_to_numeric, substitute
from ..node import ExpressionLeaf as L, Scope, OP_EQ, OP_ADD, OP_MUL, OP_DIV, \
        eq, OP_ABS, OP_AND, OP_OR
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_move_term(node):
    """
    Perform the same action on both sides of the equation such that variable
    terms are moved to the left, and constants (in relation to the variable
    that is being solved) are brought to the right side of the equation.
    If the variable is only present on the right side of the equation, swap the
    sides first.

    # Swap
    a = b * x  ->  b * x = a
    # Subtraction
    x + a = b  ->  x + a - a = b - a
    a = b + x  ->  a - x = b + x - x  # =>*  x = b / a
    # Division
    x * a = b  ->  x * a / a = b / a  # =>*  x = b / a
    # Multiplication
    x / a = b  ->  x / a * a = b * a  # =>*  x = a * b
    a / x = b  ->  a / x * x = b * x  # =>*  x = a / b
    -x = b     ->  -x * -1 = b * -1   # =>*  x = -b

    # Absolute value
    |f(x)| = c and eval(c) in Z  ->  f(x) = c vv f(x) = -c
    """
    assert node.is_op(OP_EQ)

    x = find_variable(node)
    left, right = node
    p = []

    if not left.contains(x):
        # Swap the left and right side if only the right side contains x
        if right.contains(x):
            p.append(P(node, swap_sides))

        return p

    # Bring terms without x to the right
    if left.is_op(OP_ADD):
        for n in Scope(left):
            if not n.contains(x):
                p.append(P(node, subtract_term, (n,)))

    # Bring terms with x to the left
    if right.is_op(OP_ADD):
        for n in Scope(right):
            if n.contains(x):
                p.append(P(node, subtract_term, (n,)))

    # Divide both sides by a constant to 'free' x
    if left.is_op(OP_MUL):
        for n in Scope(left):
            if not n.contains(x):
                p.append(P(node, divide_term, (n,)))

    # Multiply both sides by the denominator to move x out of the division
    if left.is_op(OP_DIV):
        p.append(P(node, multiply_term, (left[1],)))

    # Remove any negation from the left side of the equation
    if left.negated:
        p.append(P(node, multiply_term, (-L(1),)))

    # Split absolute equations into two separate, non-absolute equations
    if left.is_op(OP_ABS) and evals_to_numeric(right):
        p.append(P(node, split_absolute_equation))

    return p


def swap_sides(root, args):
    """
    a = bx  ->  bx = a
    """
    left, right = root

    return eq(right, left)


MESSAGES[swap_sides] = _('Swap the left and right side of the equation so ' \
        'that the variable is on the left side.')


def subtract_term(root, args):
    """
    x + a = b  ->  x + a - a = b - a
    a = b + x  ->  a - x = b + x - x
    """
    left, right = root
    term = args[0]

    return eq(left - term, right - term)


def subtract_term_msg(root, args):  # pragma: nocover
    term = args[0]

    if term.negated == 1:
        return _('Add %s to both sides of the equation.' % +term)

    return _('Subtract {1} from both sides of the equation.')


MESSAGES[subtract_term] = subtract_term_msg


def divide_term(root, args):
    """
    x * a = b  ->  x * a / a = b / a  # =>*  x = b / a
    """
    left, right = root
    term = args[0]

    return eq(left / term, right / term)


MESSAGES[divide_term] = _('Divide both sides of the equation by {1}.')


def multiply_term(root, args):
    """
    x / a = b  ->  x / a * a = b * a  # =>*  x = a * b
    a / x = b  ->  a / x * x = b * x  # =>*  x = a / b
    """
    left, right = root
    term = args[0]

    return eq(left * term, right * term)


MESSAGES[multiply_term] = _('Multiply both sides of the equation with {1}.')


def split_absolute_equation(root, args):
    """
    |f(x)| = c and eval(c) in Z  ->  f(x) = c vv f(x) = -c
    """
    (f,), c = root

    return eq(f, c) | eq(f, -c)


MESSAGES[split_absolute_equation] = _('Split absolute equation {0} into a ' \
                                      'negative and a positive equation.')


def match_multiple_equations(node):
    """
    Multiple equations can be solved using substitution and/or elimination.

    Substitution rule:
    x = a ^^ f(x) = g(x)  ->  x = a ^^ f(a) = g(a)  # Substitute x with a
    Substitution example:
    x = ay + b ^^ cx + dy = e  ->  x = ay + b ^^ c(ay + b) + dy = e
                             # =>*  x = eval(a * eval((e - bc) / (ca + b)) + b)
                             #      ^^ y = eval((e - bc) / (ca + b))
    """
    assert node.is_op(OP_AND)

    scope = Scope(node)
    equations = filter(lambda exp: exp.is_op(OP_EQ), scope)
    p = []

    if len(equations) < 2:
        return p

    for eq0, eq1 in permutations(equations, 2):
        x, subs = eq0

        # Substitution rule
        if x.is_variable() and eq1.contains(x):
            p.append(P(node, substitute_variable, (scope, x, subs, eq1)))

    return p


def substitute_variable(root, args):
    """
    Substitution rule:
    x = a ^^ f(x) = g(x)  ->  x = a ^^ f(a) = g(a)  # Substitute x with a
    """
    scope, x, subs, eq = args
    scope.replace(eq, substitute(eq, x, subs))

    return scope.as_nary_node()


MESSAGES[substitute_variable] = _('Substitute {2} with {3} in {4}.')


def match_double_case(node):
    """
    a ^^ a  ->  a
    a vv a  ->  a
    """
    assert node.is_op(OP_AND, OP_OR)

    scope = Scope(node)
    p = []

    for a, b in combinations(scope, 2):
        if a == b:
            p.append(P(node, double_case, (scope, a, b)))

    return p


def double_case(root, args):
    """
    a ^^ a  ->  a
    a vv a  ->  a
    """
    scope, a, b = args
    scope.remove(b)

    return scope.as_nary_node()


MESSAGES[double_case] = _('Remove double occurence of {2}.')
