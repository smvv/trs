from itertools import combinations

from ..node import ExpressionNode as N, ExpressionLeaf as L, \
                   OP_NEG, OP_MUL, OP_DIV, OP_POW, OP_ADD
from ..possibilities import Possibility as P, MESSAGES
from .utils import nary_node
from ..translate import _


def match_add_exponents(node):
    """
    a^p * a^q  ->  a^(p + q)
    a * a^q    ->  a^(1 + q)
    a^p * a    ->  a^(p + 1)
    a * a      ->  a^(1 + 1)
    """
    assert node.is_op(OP_MUL)

    p = []
    powers = {}

    for n in node.get_scope():
        if n.is_identifier():
            s = n
            exponent = L(1)
        elif n.is_op(OP_POW):
            # Order powers by their roots, e.g. a^p and a^q are put in the same
            # list because of the mutual 'a'
            s, exponent = n
        else:
            continue

        s_str = str(s)

        if s_str in powers:
            powers[s_str].append((n, exponent, s))
        else:
            powers[s_str] = [(n, exponent, s)]

    for root, occurrences in powers.iteritems():
        # If a root has multiple occurences, their exponents can be added to
        # create a single power with that root
        if len(occurrences) > 1:
            for (n0, e1, a0), (n1, e2, a1) in combinations(occurrences, 2):
                p.append(P(node, add_exponents, (n0, n1, a0, e1, e2)))

    return p


def add_exponents(root, args):
    """
    a^p * a^q  ->  a^(p + q)
    """
    n0, n1, a, p, q = args
    scope = root.get_scope()

    # Replace the left node with the new expression
    scope[scope.index(n0)] = a ** (p + q)

    # Remove the right node
    scope.remove(n1)

    return nary_node('*', scope)


MESSAGES[add_exponents] = _('Add the exponents of {1} and {2}, which'
        ' will reduce to {1[0]}^({1[1]} + {2[1]}).')


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
        return [P(node, duplicate_exponent, (left.get_scope(), right))]

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


def match_extend_exponent(node):
    """
    (a + ... + z)^n -> (a + ... + z)(a + ... + z)^(n - 1)  # n > 1
    """
    assert node.is_op(OP_POW)

    left, right = node

    if right.is_numeric():
        for n in node.get_scope():
            if n.is_op(OP_ADD):
                return [P(node, extend_exponent, (left, right))]

    return []


def extend_exponent(root, args):
    """
    (a + ... + z)^n -> (a + ... + z)(a + ... + z)^(n - 1)  # n > 1
    """
    left, right = args

    if right.value > 2:
        return left * left ** L(right.value - 1)

    return left * left


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
