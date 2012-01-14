from itertools import combinations

from .utils import nary_node
from ..node import ExpressionLeaf as Leaf, OP_DIV, OP_MUL
from ..possibilities import Possibility as P, MESSAGES


def add_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary addition.

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


#def match_subtract_numerics(node):
#    """
#    3 - 2      ->  2.0
#    3.0 - 2    ->  1.0
#    3 - 2.0    ->  1.0
#    3.0 - 2.0  ->  1.0
#    """
#    # TODO: This should be handled by match_combine_polynomes
#    assert node.is_op(OP_MUL)


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


def match_multiply_numerics(node):
    """
    3 * 2      ->  6
    3.0 * 2    ->  6.0
    3 * 2.0    ->  6.0
    3.0 * 2.0  ->  6.0
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = node.get_scope()
    numerics = filter(lambda n: n.is_numeric(), scope)

    for args in combinations(numerics, 2):
        p.append(P(node, multiply_numerics, args))

    return p


def multiply_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary multiplication.

    Example:
    2 * 3  ->  6
    """
    n0, n1 = args
    scope = []

    for n in root.get_scope():
        if hash(n) == hash(n0):
            # Replace the left node with the new expression
            scope.append(Leaf(n0.value * n1.value))
            #scope.append(n)
        elif hash(n) != hash(n1):
            # Remove the right node
            scope.append(n)

    return nary_node('*', scope)
