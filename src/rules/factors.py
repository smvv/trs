from itertools import product, combinations

from .utils import nary_node
from ..node import OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES


def match_expand(node):
    """
    a * (b + c) -> ab + ac
    (b + c) * a -> ab + ac
    (a + b) * (c + d) -> ac + ad + bc + bd
    """
    assert node.is_op(OP_MUL)

    p = []
    leaves = []
    additions = []

    for n in node.get_scope():
        if n.is_leaf():
            leaves.append(n)
        elif n.op == OP_ADD:
            additions.append(n)

    for args in product(leaves, additions):
        p.append(P(node, expand_single, args))

    for args in combinations(additions, 2):
        p.append(P(node, expand_double, args))

    return p


def expand_single(root, args):
    """
    Combine a leaf (a) multiplied with an addition of two expressions
    (b + c) to an addition of two multiplications.

    a * (b + c) -> ab + ac
    (b + c) * a -> ab + ac
    """
    a, bc = args
    b, c = bc
    scope = root.get_scope()

    # Replace 'a' with the new expression
    scope[scope.index(a)] = a * b + a * c

    # Remove the addition
    scope.remove(bc)

    return nary_node('*', scope)


def expand_double(root, args):
    """
    Rewrite two multiplied additions to an addition of four multiplications.

    (a + b) * (c + d) -> ac + ad + bc + bd
    """
    (a, b), (c, d) = ab, cd = args
    scope = root.get_scope()

    # Replace 'b + c' with the new expression
    scope[scope.index(ab)] = a * c + a * d + b * c + b * d

    # Remove the right addition
    scope.remove(cd)

    return nary_node('*', scope)
