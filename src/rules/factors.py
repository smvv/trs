from ..node import OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from .utils import nary_node


def match_expand(node):
    """
    a * (b + c) -> ab + ac
    """
    assert node.is_op(OP_MUL)

    # TODO: fix!
    return []

    p = []
    a = []
    bc = []

    for n in node.get_scope():
        if n.is_leaf():
            a.append(n)
        elif n.op == OP_ADD:
            bc.append(n)

    if a and bc:
        for a_node in a:
            for bc_node in bc:
                p.append(P(node, expand_single, a_node, bc_node))

    return p


def expand_single(root, args):
    """
    Combine a leaf (a) multiplied with an addition of two expressions
    (b + c) to an addition of two multiplications.

    >>> a * (b + c) -> a * b + a * c
    """
    a, bc = args
    b, c = bc
    scope = root.get_scope()

    # Replace 'a' with the new expression
    scope[scope.index(a)] = a * b + a * c

    # Remove the old addition
    scope.remove(bc)

    return nary_node('*', scope)
