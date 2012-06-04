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
from .utils import iter_pairs, evals_to_numeric
from ..node import ExpressionNode as N, Scope, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def get_power_prop(node):
    """
    Get the power properties of a node needed for sorting, being the variable
    name and exponent value.
    """
    if node.is_variable():
        return node.value, 1

    if node.is_power():
        root, exponent = node

        if root.is_variable():
            if exponent.is_numeric():
                # Numeric exponent: value can be compared to other exponents
                exp = exponent.actual_value()
            else:
                # No numeric exponent: same precedence as the variable itself
                exp = 1

            return root.value, exp


def is_upper(character):
    return 'A' <= character <= 'Z'


def swap_mono((left, right)):
    """
    Check if a pair of left and right multiplication factors in a monomial
    should be swapped to be correctly sorted.
    """
    # Numerics should always be on the left of a monomial
    if evals_to_numeric(right):
        return not evals_to_numeric(left)

    left_prop = get_power_prop(left)
    right_prop = get_power_prop(right)

    if left_prop and right_prop:
        left_var, left_exp = left_prop
        right_var, right_exp = right_prop

        if left_var == right_var:
            # Same variable, compare exponents
            return left_exp > right_exp

        if is_upper(left_var) != is_upper(right_var):
            return is_upper(left_var) < is_upper(right_var)

        # Compare variable names alphabetically
        return left_var > right_var

    return False


def get_poly_prop(node):
    """
    Get the polynome properties of an monomial in a polynome, being the leading
    variable name and the exponent it is raised to.
    """
    if node.is_op(OP_MUL):
        scope = Scope(node)
        power = None

        for n in scope:
            new_power = get_power_prop(n)

            if new_power:
                if not power:
                    var, exp = power = new_power
                    continue

                new_var, new_exp = new_power

                if (new_exp > exp if new_var == var else new_var < var):
                    var, exp = power = new_power

        return power

    return get_power_prop(node)


def swap_poly((left, right)):
    """
    Check if a pair of left and right addition factors in a polynomial should
    be swapped to be correctly sorted.
    """
    left_poly = get_poly_prop(left)
    right_poly = get_poly_prop(right)

    if not left_poly:
        return bool(right_poly)
    elif not right_poly:
        return False

    left_var, left_exp = left_poly
    right_var, right_exp = right_poly

    if left_var == right_var:
        # Same variable, compare exponents
        return left_exp < right_exp

    if is_upper(left_var) != is_upper(right_var):
        return is_upper(left_var) > is_upper(right_var)

    # Compare variable names alphabetically
    return left_var > right_var


def match_sort_monomial(node):
    """
    Sort a monomial, pursuing the following form:
    x^0 * x^1 * ... * x^n
    For example: 2xx^2
    """
    assert node.is_op(OP_MUL)

    scope = Scope(node)

    return [P(node, swap_factors, (scope, l, r))
            for l, r in filter(swap_mono, iter_pairs(scope))]


def match_sort_polynome(node):
    """
    Sort a polynome, pursuing the following form:
    c_n * x^n * ... * c_1 * x^1 * c_0 * x^0
    For example: 2x^2 + x - 3
    """
    assert node.is_op(OP_ADD)

    scope = Scope(node)

    return [P(node, swap_factors, (scope, l, r))
            for l, r in filter(swap_poly, iter_pairs(scope))]


def swap_factors(root, args):
    """
    f * g  ->  g * f
    """
    scope, left, right = args

    scope.replace(left, N(root.op, right, left))
    scope.remove(right)

    return scope.as_nary_node()


MESSAGES[swap_factors] = _('Move {3} to the left of {2}.')
