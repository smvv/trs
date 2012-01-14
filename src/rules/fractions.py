from itertools import combinations

from .utils import nary_node, least_common_multiple
from ..node import ExpressionLeaf as L, OP_DIV, OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_constant_division(node):
    """
    a / 0  ->  Division by zero
    a / 1  ->  a
    0 / a  ->  0
    a / a  ->  1
    """
    assert node.is_op(OP_DIV)

    p = []
    nominator, denominator = node

    # a / 0
    # TODO: move to parser
    if denominator == 0:
        raise ZeroDivisionError()

    # a / 1
    if denominator == 1:
        p.append(P(node, division_by_one, (nominator,)))

    # 0 / a
    if nominator == 0:
        p.append(P(node, division_of_zero))

    # a / a
    if nominator == denominator:
        p.append(P(node, division_by_self))

    return p


def division_by_one(root, args):
    """
    a / 1  ->  a
    """
    return args[0]


def division_of_zero(root, args):
    """
    0 / a  ->  0
    """
    return L(0)


def division_by_self(root, args):
    """
    a / a  ->  1
    """
    return L(1)


def match_add_constant_fractions(node):
    """
    1 / 2 + 3 / 4  ->  2 / 4 + 3 / 4  # Equalize denominators
    2 / 4 + 3 / 4  ->  5 / 4          # Equal denominators, so nominators can
                                      # be added
    """
    assert node.is_op(OP_ADD)

    p = []
    fractions = filter(lambda n: n.is_op(OP_DIV), node.get_scope())

    for a, b in combinations(fractions, 2):
        na, da = a
        nb, db = b

        if da == db:
            # Equal denominators, add nominators to create a single fraction
            p.append(P(node, add_nominators, (a, b)))
        elif da.is_numeric() and db.is_numeric():
            # Denominators are both numeric, rewrite both fractions to the
            # least common multiple of their denominators. Later, the
            # nominators will be added
            denom = least_common_multiple(da.value, db.value)
            p.append(P(node, equalize_denominators, (a, b, denom)))

    return p


def equalize_denominators(root, args):
    """
    1 / 2 + 3 / 4  ->  2 / 4 + 3 / 4
    a / 2 + b / 4  ->  2a / 4 + b / 4
    """
    denom = args[2]

    scope = root.get_scope()

    for fraction in args[:2]:
        n, d = fraction
        mult = denom / d.value

        if mult != 1:
            n = L(n.value * mult) if n.is_numeric() else L(mult) * n
            scope[scope.index(fraction)] = n / L(d.value * mult)

    return nary_node('+', scope)


def add_nominators(root, args):
    """
    a / b + c / b  ->  (a + c) / b
    """
    ab, cb = args
    a, b = ab
    c = cb[0]

    scope = root.get_scope()

    # Replace the left node with the new expression
    scope[scope.index(ab)] = (a + c) / b

    # Remove the right node
    scope.remove(cb)

    return nary_node('+', scope)


def match_expand_and_add_fractions(node):
    """
    a * b / c + d * b / c  ->  (a + d) * (b / c)
    """
    assert node.is_op(OP_MUL)

    p = []

    return p
