from itertools import product, combinations

from ..node import Scope, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_expand(node):
    """
    a(b + c)        ->  ab + ac
    (b + c)a        ->  ab + ac
    (a + b)(c + d)  ->  ac + ad + bc + bd
    """
    assert node.is_op(OP_MUL)

    p = []
    leaves = []
    additions = []
    scope = Scope(node)

    for n in scope:
        if n.is_leaf:
            leaves.append(n)
        elif n.op == OP_ADD:
            # If the addition only contains numerics, do not expand
            if not filter(lambda n: not n.is_numeric(), Scope(n)):
                continue

            additions.append(n)

    for l, a in product(leaves, additions):
        p.append(P(node, expand_single, (scope, l, a)))

    for a0, a1 in combinations(additions, 2):
        p.append(P(node, expand_double, (scope, a0, a1)))

    return p


def expand_single(root, args):
    """
    Combine a leaf (a) multiplied with an addition of two expressions
    (b + c) to an addition of two multiplications.

    a(b + c)  ->  ab + ac
    (b + c)a  ->  ab + ac
    """
    scope, a, bc = args
    b, c = bc

    # Replace 'a' with the new expression
    scope.replace(a, a * b + a * c)

    # Remove the addition
    scope.remove(bc)

    return scope.as_nary_node()


MESSAGES[expand_single] = _('Expand {1}({2}).')


def expand_double(root, args):
    """
    Rewrite two multiplied additions to an addition of four multiplications.

    (a + b)(c + d)  ->  ac + ad + bc + bd
    """
    scope, ab, cd = args
    (a, b), (c, d) = ab, cd

    # Replace 'a + b' with the new expression
    scope.replace(ab, a * c + a * d + b * c + b * d)

    # Remove the right addition
    scope.remove(cd)

    return scope.as_nary_node()


MESSAGES[expand_double] = _('Expand ({1})({2}).')
