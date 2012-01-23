from itertools import combinations

from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, \
                   OP_NEG, OP_MUL, OP_DIV, OP_POW
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_exponents(node):
    """
    a^p * a^q  ->  a^(p + q)
    """
    assert node.is_op(OP_MUL)

    p = []
    powers = {}

    for n in Scope(node):
        if n.is_op(OP_POW):
            # Order powers by their roots, e.g. a^p and a^q are put in the same
            # list because of the mutual 'a'
            s = str(n[0])

            if s in powers:
                powers[s].append(n)
            else:
                powers[s] = [n]

    for root, occurrences in powers.iteritems():
        # If a root has multiple occurences, their exponents can be added to
        # create a single power with that root
        if len(occurrences) > 1:
            for pair in combinations(occurrences, 2):
                p.append(P(node, add_exponents, pair))

    return p


def match_subtract_exponents(node):
    """
    a^p / a^q  ->  a^(p - q)
    a^p / a    ->  a^(p - 1)
    a / a^q    ->  a^(1 - q)
    """
    assert node.is_op(OP_DIV)

    left, right = node
    left_pow, right_pow = left.is_op(OP_POW), right.is_op(OP_POW)

    if left_pow and right_pow and left[0] == right[0]:
        # A power is divided by a power with the same root
        return [P(node, subtract_exponents, tuple(left) + (right[1],))]

    if left_pow and left[0] == right:
        # A power is divided by a its root
        return [P(node, subtract_exponents, tuple(left) + (1,))]

    if right_pow and left == right[0]:
        # An identifier is divided by a power of itself
        return [P(node, subtract_exponents, (left, 1, right[1]))]

    return []


def match_multiply_exponents(node):
    """
    (a^p)^q  ->  a^(pq)
    """
    assert node.is_op(OP_POW)

    left, right = node

    if left.is_op(OP_POW):
        return [P(node, multiply_exponents, tuple(left) + (right,))]

    return []


def match_duplicate_exponent(node):
    """
    (ab)^p  ->  a^p * b^p
    """
    assert node.is_op(OP_POW)

    left, right = node

    if left.is_op(OP_MUL):
        return [P(node, duplicate_exponent, (Scope(left), right))]

    return []


def match_remove_negative_exponent(node):
    """
    a^-p  ->  1 / a^p
    """
    assert node.is_op(OP_POW)

    left, right = node

    if right.is_op(OP_NEG):
        return [P(node, remove_negative_exponent, (left, right[0]))]

    return []


def match_exponent_to_root(node):
    """
    a^(1 / m)  ->  sqrt(a, m)
    a^(n / m)  ->  sqrt(a^n, m)
    """
    assert node.is_op(OP_POW)

    left, right = node

    if right.is_op(OP_DIV):
        return [P(node, exponent_to_root, (left,) + tuple(right))]

    return []


def add_exponents(root, args):
    """
    a^p * a^q  ->  a^(p + q)
    """
    n0, n1 = args
    a, p = n0
    q = n1[1]
    scope = Scope(root)

    # Replace the left node with the new expression
    scope.remove(n0, a ** (p + q))

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[add_exponents] = _('Add the exponents of {1} and {2}, which'
        ' will reduce to {1[0]}^({1[1]} + {2[1]}).')


def subtract_exponents(root, args):
    """
    a^p / a^q  ->  a^(p - q)
    """
    a, p, q = args

    return a ** (p - q)


MESSAGES[subtract_exponents] = _('Substract the exponents {1} and {2},'
        ' which will reduce to {1[0]}^({1[1]} - {2[1]}).')


def multiply_exponents(root, args):
    """
    (a^p)^q  ->  a^(pq)
    """
    a, p, q = args

    return a ** (p * q)


MESSAGES[multiply_exponents] = _('Multiply the exponents {1} and {2},'
        ' which will reduce to {1[0]}^({1[1]} * {2[1]}).')


def duplicate_exponent(root, args):
    """
    (ab)^p   ->  a^p * b^p
    (abc)^p  ->  a^p * b^p * c^p
    """
    ab, p = args
    result = ab[0] ** p

    for b in ab[1:]:
        result *= b ** p

    return result


MESSAGES[duplicate_exponent] = _('Duplicate the exponents {1} and {2},'
        ' which will reduce to {1[0]}^({1[1]} * {2[1]}).')


def remove_negative_exponent(root, args):
    """
    a^-p  ->  1 / a^p
    """
    a, p = args

    return L(1) / a ** p


def exponent_to_root(root, args):
    """
    a^(1 / m)  ->  sqrt(a, m)
    a^(n / m)  ->  sqrt(a^n, m)
    """
    a, n, m = args

    return N('sqrt', a if n == 1 else a ** n, m)
