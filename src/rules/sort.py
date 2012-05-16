from .utils import iter_pairs
from ..node import ExpressionNode as N, Scope, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def swap_moni((left, right)):
    left_num, right_num = left.is_numeric(), right.is_numeric()

    if left_num and right_num:
        return False

    left_var, right_var = left.is_variable(), right.is_variable()

    if left_var and right_var:
        return cmp(left.value, right.value)

    if left_var and right_num:
        return True


def swap_poly((left, right)):
    pass


def match_sort_polynome(node):
    """
    """
    assert node.is_op(OP_ADD)

    scope = Scope(node)

    return [P(node, swap_factors, (scope, l, r))
            for l, r in filter(swap_poly, iter_pairs(scope))]


def match_sort_molinome(node):
    """
    x * 2          ->  2x             # variable > number
    x ^ 2 * x ^ 3  ->  x ^ 3 * x ^ 2  # exponents
    yx             ->  xy             # alphabetically
    """
    assert node.is_op(OP_MUL)

    scope = Scope(node)

    return [P(node, swap_factors, (scope, l, r))
            for l, r in filter(swap_moni, iter_pairs(scope))]


def swap_factors(root, args):
    """
    left * right
    """
    scope, left, right = args

    scope.replace(left, N(root.op, right, left))
    scope.remove(right)

    return scope.as_nary_node()


MESSAGES[swap_factors] = _('Move {2} to the left of {1}.')
