from itertools import combinations

from ..node import OP_ADD, OP_NEG
from ..possibilities import Possibility as P, MESSAGES
from .utils import nary_node
from .numerics import add_numerics


def is_numeric_or_negated_numeric(n):
    return n.is_numeric() or (n.is_op(OP_NEG) and n[0].is_numeric())


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
                    and all(map(is_numeric_or_negated_numeric, [r0, r1])):
                # 2 + 3    ->  5
                # 2 + -3   ->  -1
                # -2 + 3   ->  1
                # -2 + -3  ->  -5
                p.append(P(node, add_numerics, (n0, n1, r0, r1)))
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
