from itertools import product, combinations

from ..node import Scope, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


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

    for n in Scope(node):
        if n.is_leaf:
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
    scope = Scope(root)

    # Replace 'a' with the new expression
    scope.remove(a, a * b + a * c)

    # Remove the addition
    scope.remove(bc)

    return scope.as_nary_node()


MESSAGES[expand_single] = _('Expand {1}({2}).')


def expand_double(root, args):
    """
    Rewrite two multiplied additions to an addition of four multiplications.

    (a + b) * (c + d) -> ac + ad + bc + bd
    """
    (a, b), (c, d) = ab, cd = args
    scope = Scope(root)

    # Replace 'a + b' with the new expression
    scope.remove(ab, a * c + a * d + b * c + b * d)

    # Remove the right addition
    scope.remove(cd)

    return scope.as_nary_node()


MESSAGES[expand_double] = _('Expand ({1})({2}).')
