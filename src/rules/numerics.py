from ..node import ExpressionLeaf as Leaf, OP_DIV, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from .utils import nary_node


def match_divide_numerics(node):
    """
    Combine two constants to a single constant in a division, if it does not
    lead to a decrease in precision.

    Example:
    6 / 2      ->  3
    3 / 2      ->  3 / 2  # 1.5 would mean a decrease in precision
    3.0 / 2    ->  1.5
    3 / 2.0    ->  1.5
    3.0 / 2.0  ->  1.5
    3 / 1.0    ->  3      # Exceptional case: division of integer by 1.0 keeps
                          # integer precision
    """
    assert node.is_op(OP_DIV)

    n, d = node
    divide = False
    dv = d.value

    if n.is_int() and d.is_int():
        # 6 / 2  ->  3
        # 3 / 2  ->  3 / 2
        divide = not divmod(n.value, dv)[1]
    elif n.is_numeric() and d.is_numeric():
        if d == 1.0:
            # 3 / 1.0  ->  3
            dv = 1

        # 3.0 / 2  ->  1.5
        # 3 / 2.0  ->  1.5
        # 3.0 / 2.0  ->  1.5
        divide = True

    return [P(node, divide_numerics, (n.value, dv))] if divide else []


def match_multiply_numerics(node):
    """
    3 * 2      ->  6
    3.0 * 2    ->  6.0  # FIXME: is this correct?
    3 * 2.0    ->  6.0  # FIXME: is this correct?
    3.0 * 2.0  ->  6.0
    """
    # TODO: Finish
    assert node.is_op(OP_MUL)


def match_subtract_numerics(node):
    """
    3 - 2      ->  2.0
    3.0 - 2    ->  1.0  # FIXME: is this correct?
    3 - 2.0    ->  1.0  # FIXME: is this correct?
    3.0 - 2.0  ->  1.0
    """
    # TODO: Finish
    assert node.is_op(OP_MUL)


def divide_numerics(root, args):
    """
    Combine two constants to a single constant in a division.

    Examples:
    6 / 2      ->  3
    3.0 / 2    ->  1.5
    3 / 2.0    ->  1.5
    3.0 / 2.0  ->  1.5
    3 / 1.0    ->  3
    """
    n, d = args

    return Leaf(n / d)


def add_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary plus.

    Example:
    2 + 3  ->  5
    """
    n0, n1, c0, c1 = args

    scope = root.get_scope()

    # Replace the left node with the new expression
    scope[scope.index(n0)] = Leaf(c0 + c1)

    # Remove the right node
    scope.remove(n1)

    return nary_node('+', scope)
