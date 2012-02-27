from itertools import combinations

from .utils import least_common_multiple
from ..node import ExpressionLeaf as L, Scope, negate, OP_DIV, OP_ADD, OP_MUL
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
    if denominator == 0:
        raise ZeroDivisionError('Division by zero: %s.' % node)

    # a / 1
    if denominator == 1:
        p.append(P(node, division_by_one, (nominator,)))

    # 0 / a
    if nominator == 0:
        p.append(P(node, division_of_zero, (denominator,)))

    # a / a
    if nominator == denominator:
        p.append(P(node, division_by_self, (nominator,)))

    return p


def division_by_one(root, args):
    """
    a / 1  ->  a
    """
    return args[0]


MESSAGES[division_by_one] = _('Division of {1} by 1 reduces to {1}.')


def division_of_zero(root, args):
    """
    0 / a  ->  0
    """
    return L(0)


MESSAGES[division_of_zero] = _('Division of 0 by {1} reduces to 0.')


def division_by_self(root, args):
    """
    a / a  ->  1
    """
    return L(1)


MESSAGES[division_by_self] = _('Division of {1} by {1} reduces to 1.')


def match_add_constant_fractions(node):
    """
    1 / 2 + 3 / 4  ->  2 / 4 + 3 / 4  # Equalize denominators
    2 / 2 - 3 / 4  ->  4 / 4 - 3 / 4
    2 / 4 + 3 / 4  ->  5 / 4          # Equal denominators, so nominators can
                                      # be added
    2 / 4 - 3 / 4  ->  -1 / 4
    1 / 2 + 3 / 4  ->  4 / 8 + 6 / 8  # Equalize denominators by multiplying
                                      # them with eachother

    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)

    fractions = filter(lambda node: node.is_op(OP_DIV), scope)

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
            p.append(P(node, equalize_denominators, (scope, a, b, denom)))

            # Also, add the (non-recommended) possibility to multiply the
            # denominators
            p.append(P(node, equalize_denominators, (scope, a, b,
                                                     da.value * db.value)))

    return p


def equalize_denominators(root, args):
    """
    1 / 2 + 3 / 4  ->  2 / 4 + 3 / 4
    a / 2 + b / 4  ->  2a / 4 + b / 4
    """
    scope, denom = args[::3]

    for fraction in args[1:3]:
        n, d = fraction
        mult = denom / d.value

        if mult != 1:
            if n.is_numeric():
                n = L(n.value * mult)
            else:
                n = L(mult) * n

            #n = L(n.value * mult) if n.is_numeric() else L(mult) * n

            scope.replace(fraction, negate(n / L(d.value * mult),
                                           fraction.negated))

    return scope.as_nary_node()


MESSAGES[equalize_denominators] = _('Equalize the denominators of divisions'
    ' {2} and {3} to {4}.')


def add_nominators(root, args):
    """
    a / b + c / b      ->  (a + c) / b
    a / b - c / b      ->  (a - c) / b
    -(a / b) + c / b   ->  -((a + c) / b)
    -(a / b) - c / b   ->  (c - a) / -b
    """
    # TODO: is 'add' Appropriate when rewriting to "(a + (-c)) / b"?
    ab, cb = args
    a, b = ab
    scope = Scope(root)

    # Replace the left node with the new expression
    scope.replace(ab, (a + cb[0].negate(cb.negated)) / b)

    # Remove the right node
    scope.remove(cb)

    return scope.as_nary_node()


# TODO: convert this to a lambda. Example: 22 / 77 - 28 / 77. the "-" is above
# the "28/77" division.
MESSAGES[add_nominators] = _('Add the nominators of {1} and {2}.')


def match_expand_and_add_fractions(node):
    """
    a * b / c + d * b / c      ->  (a + d) * (b / c)
    a * b / c + (- d * b / c)  ->  (a + (-d)) * (b / c)
    """
    # TODO: is 'add' Appropriate when rewriting to "(a + (-d)) / * (b / c)"?
    assert node.is_op(OP_MUL)

    p = []

    return p
