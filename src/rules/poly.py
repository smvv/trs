from itertools import combinations

from ..node import ExpressionNode as Node, ExpressionLeaf as Leaf, \
        OP_ADD, OP_MUL
from ..possibilities import Possibility as P
from .utils import nary_node
from .numerics import add_numerics


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
    assert node.is_op(OP_ADD)

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
            n0, p0 = left
            n1, p1 = right
            c0, r0, e0 = p0
            c1, r1, e1 = p1

            # Both numeric root and same exponent -> combine coefficients and
            # roots, or: same root and exponent -> combine coefficients.
            # TODO: Addition with zero, e.g. a + 0 -> a
            if c0 == 1 and c1 == 1 and e0 == 1 and e1 == 1 \
                    and r0.is_numeric() and r1.is_numeric():
                # 2 + 3 -> 5
                p.append(P(node, add_numerics, (n0, n1, r0.value, r1.value)))
            elif c0.is_numeric() and c1.is_numeric() and r0 == r1 and e0 == e1:
                # 2a + 2a -> 4a
                # a + 2a -> 3a
                # 2a + a -> 3a
                # a + a -> 2a
                p.append(P(node, combine_polynomes, (n0, n1, c0, c1, r0, e0)))

    return p


def combine_polynomes(root, args):
    """
    Combine two multiplications of any polynome in an n-ary plus.

    Synopsis:
    c0 * a ^ b + c1 * a ^ b -> (c0 + c1) * a ^ b
    """
    n0, n1, c0, c1, r, e = args

    # a ^ 1 -> a
    power = r if e == 1 else r ^ e

    # replacement: (c0 + c1) * a ^ b
    # a, b and c are from 'left', d is from 'right'.
    replacement = (c0 + c1) * power

    scope = root.get_scope()

    # Replace the left node with the new expression
    scope[scope.index(n0)] = replacement

    # Remove the right node
    scope.remove(n1)

    return nary_node('+', scope)
