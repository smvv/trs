from itertools import combinations

from ..node import ExpressionNode as Node, TYPE_OPERATOR, OP_ADD, OP_MUL
from ..possibilities import Possibility as P
from .utils import nary_node


def match_expand(node):
    """
    a * (b + c) -> ab + ac
    """
    assert node.type == TYPE_OPERATOR
    assert node.op == OP_MUL

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
    scope[scope.index(a)] = Node('+', Node('*', a, b), \
                                      Node('*', a, c))

    # Remove the old addition
    scope.remove(bc)

    return nary_node('*', scope)


def match_combine_polynomes(node, verbose=False):
    """
    n + exp + m -> exp + (n + m)
    k0 * v ^ n + exp + k1 * v ^ n -> exp + (k0 + k1) * v ^ n
    """
    assert node.type == TYPE_OPERATOR
    assert node.op == OP_ADD

    p = []

    # Collect all nodes that can be combined:
    # a ^ e     = 1 * a ^ e
    # c * a     = c * a ^ 1
    # c * a ^ e
    # a         = 1 * a ^ 1
    #
    # Identifier nodes of all polynomes, tuple format is:
    #   (root, exponent, coefficient, literal_coefficient)
    polys = []

    if verbose:  # pragma: nocover
        print 'match combine factors:', node

    for n in node.get_scope():
        polynome = n.extract_polynome_properties()

        if verbose:  # pragma: nocover
            print 'n:', n, 'polynome:', polynome

        if polynome:
            polys.append((n, polynome))

    # Each combination of powers of the same value and polynome can be added
    if len(polys) >= 2:
        for left, right in combinations(polys, 2):
            c0, r0, e0 = left[1]
            c1, r1, e1 = right[1]

            # Both numeric root and same exponent -> combine coefficients and
            # roots, or: same root and exponent -> combine coefficients.
            if c0 == 1 and c1 == 1 and e0 == 1 and e1 == 1 \
                    and r0.is_numeric() and r1.is_numeric():
                # 2 + 3 -> 5
                p.append(P(node, combine_numerics, \
                           (left[0], right[0], r0, r1)))
            elif c0.is_numeric() and c1.is_numeric() and r0 == r1 and e0 == e1:
                # 2a + 2a -> 4a
                # a + 2a -> 3a
                # 2a + a -> 3a
                # a + a -> 2a
                p.append(P(node, combine_polynomes, \
                           (left[0], right[0], c0, c1, r0, e0)))

    return p


def combine_polynomes(root, args):
    """
    Combine two multiplications of any polynome in an n-ary plus.

    Example:
    c * a ^ b + d * a ^ b -> (c + d) * a ^ b
    """
    left, right = args
    nl, pl = left
    nr, pr = right

    # TODO: verify that the two commented expression below are invalid and the
    # following two expressions are right.
    c0, r0, e0 = pl
    c1, r1, e1 = pr

    #if r0.is_numeric() and r1.is_numeric() and e0 == e1 == 1:
    #    new_root = Leaf(r0.value + r1.value)
    #else:
    #    new_root = r0

    if pl[3] or pr[3]:
        # literal a ^ 1 -> a ^ 1
        power = Node('^', pl[0], pl[1])
    else:
        # nonliteral a ^ 1 -> a
        power = pl[0]

    # replacement: (c + d) * a ^ b
    # a, b and c are from 'left', d is from 'right'.
    replacement = Node('*', Node('+', pl[2], pr[2]), power)

    scope = root.get_scope()

    # Replace the left node with the new expression
    scope[scope.index(nl)] = replacement

    # Remove the right node
    scope.remove(nr)

    return nary_node('+', scope)
