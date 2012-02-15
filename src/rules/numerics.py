from itertools import combinations

from ..node import ExpressionLeaf as Leaf, Scope, negate, OP_DIV, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def add_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary addition.

    Example:
    2 + 3    ->  5
    2 + -3   ->  -1
    -2 + 3   ->  1
    -2 + -3  ->  -5
    """
    n0, n1, c0, c1 = args
    scope = Scope(root)

    # Replace the left node with the new expression
    scope.remove(n0, Leaf(c0.actual_value() + c1.actual_value()))

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[add_numerics] = _('Combine the constants {1} and {2}.')


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


MESSAGES[divide_numerics] = _('Divide constant {1} by constant {2}.')


def match_multiply_zero(node):
    """
    a * 0    ->  0
    0 * a    ->  0
    -0 * a   ->  -0
    0 * -a   ->  -0
    -0 * -a  ->  0
    """
    assert node.is_op(OP_MUL)

    left, right = node

    if (left.is_leaf and left.value == 0) \
            or (right.is_leaf and right.value == 0):
        return [P(node, multiply_zero, (left.negated + right.negated,))]

    return []


def multiply_zero(root, args):
    """
    a * 0  ->  0
    0 * a  ->  0
    -0 * a   ->  -0
    0 * -a   ->  -0
    -0 * -a  ->  0
    """
    return negate(Leaf(0), args[0])


MESSAGES[multiply_zero] = _('Multiplication with zero yields zero.')


def match_multiply_numerics(node):
    """
    3 * 2      ->  6
    3.0 * 2    ->  6.0
    3 * 2.0    ->  6.0
    3.0 * 2.0  ->  6.0
    """
    assert node.is_op(OP_MUL)

    p = []
    numerics = []

    for n in Scope(node):
        if n.is_numeric():
            numerics.append((n, n.actual_value()))

    for (n0, v0), (n1, v1) in combinations(numerics, 2):
        p.append(P(node, multiply_numerics, (n0, n1, v0, v1)))

    return p


def multiply_numerics(root, args):
    """
    Combine two constants to a single constant in an n-ary multiplication.

    Example:
    2 * 3  ->  6
    """
    n0, n1, v0, v1 = args
    scope = []
    value = v0 * v1

    if value > 0:
        substitution = Leaf(value)
    else:
        substitution = -Leaf(-value)

    scope = Scope(root)

    # Replace the left node with the new expression
    scope.remove(n0, substitution)

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[multiply_numerics] = _('Multiply constant {1} with {2}.')
