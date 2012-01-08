from ..node import ExpressionLeaf as Leaf, TYPE_INTEGER, TYPE_FLOAT, OP_DIV
from ..possibilities import Possibility as P
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
    n_int = n.type == TYPE_INTEGER
    n_float = n.type == TYPE_FLOAT
    d_int = d.type == TYPE_INTEGER
    d_float = d.type == TYPE_FLOAT
    nv, dv = n.value, d.value
    divide = False

    if n_int and d_int:
        # 6 / 2  ->  3
        # 3 / 2  ->  3 / 2
        divide = not divmod(nv, dv)[1]
    else:
        if d_float and dv == 1.0:
            # 3 / 1.0  ->  3
            dv = 1

        # 3.0 / 2  ->  1.5
        # 3 / 2.0  ->  1.5
        # 3.0 / 2.0  ->  1.5
        divide = True

    return [P(node, divide_numerics, (nv, dv))] if divide else []


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
