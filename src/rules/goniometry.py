from itertools import permutations

from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_ADD, OP_MUL, \
        OP_DIV, OP_SIN, OP_COS, OP_TAN, OP_SQRT, PI, TYPE_OPERATOR, sin, cos, \
        Scope
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_quadrants(node):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)

    for sin_q, cos_q in permutations(scope, 2):
        if sin_q.is_power(2) and cos_q.is_power(2) \
                and not sin_q.negated and not cos_q.negated:
            s, c = sin_q[0], cos_q[0]

            if s.is_op(OP_SIN) and c.is_op(OP_COS) and not s.negated \
                    and not c.negated and s[0] == c[0]:
                p.append(P(node, add_quadrants, (scope, sin_q, cos_q)))

    return p


def add_quadrants(root, args):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    scope, s, c = args
    scope.replace(s, L(1))
    scope.remove(c)

    return scope.as_nary_node()


MESSAGES[add_quadrants] = _('Add the sinus and cosinus quadrants to 1.')


def match_negated_parameter(node):
    """
    sin(-t)  ->  -sin(t)
    cos(-t)  ->  cos(t)
    """
    assert node.is_op(OP_SIN) or node.is_op(OP_COS)

    t = node[0]

    if t.negated:
        if node.op == OP_SIN:
            return [P(node, negated_sinus_parameter, (t,))]

        return [P(node, negated_cosinus_parameter, (t,))]

    return []


def negated_sinus_parameter(root, args):
    """
    sin(-t)  ->  -sin(t)
    """
    return -sin(+args[0])


MESSAGES[negated_sinus_parameter] = \
        _('Bring the negation from the sinus parameter {1} to the outside.')


def negated_cosinus_parameter(root, args):
    """
    cos(-t)  ->  cos(t)
    """
    return cos(+args[0])


MESSAGES[negated_cosinus_parameter] = \
        _('Remove the negation from the cosinus parameter {1}.')


def match_half_pi_subtraction(node):
    """
    sin(pi / 2 - t)  ->  cos(t)
    cos(pi / 2 - t)  ->  sin(t)
    """
    assert node.is_op(OP_SIN) or node.is_op(OP_COS)

    if node[0].is_op(OP_ADD):
        half_pi, t = node[0]

        if half_pi == L(PI) / 2:
            if node.op == OP_SIN:
                return [P(node, half_pi_subtraction_sinus, (t,))]

    return []


def half_pi_subtraction_sinus(root, args):
    pass


def is_pi_frac(node, denominator):
    """
    Check if a node is a fraction of 1 multiplied with PI.

    Example:
    >>> print is_pi_frac(L(1) / 2 * L(PI), 2)
    True
    """
    if not node.is_op(OP_MUL):
        return False

    frac, pi = node

    if not frac.is_op(OP_DIV) or not pi.is_leaf or pi.value != PI:
        return False

    n, d = frac

    return n == 1 and d == denominator


def sqrt(value):
    return N(OP_SQRT, L(value))


l0, l1, sq2, sq3 = L(0), L(1), sqrt(2), sqrt(3)
half = l1 / 2

CONSTANTS = {
    OP_SIN: [l0, half, half * sq2, half * sq3, l1],
    OP_COS: [l1, half * sq3, half * sq2, half, l0],
    OP_TAN: [l0, l1 / 3 * sq3, l1, sq3]
}


def match_standard_radian(node):
    """
    Apply a direct constant calculation from the constants table:

        | 0 | pi / 6    | pi / 4    | pi / 3    | pi / 2
    ----+---+-----------+-----------+-----------+-------
    sin | 0 | 1/2       | sqrt(2)/2 | sqrt(3)/2 | 1
    cos | 1 | sqrt(3)/2 | sqrt(2)/2 | 1/2       | 0
    tan | 0 | sqrt(3)/3 | 1         | sqrt(3)   | -
    """
    assert node.type == TYPE_OPERATOR and node.op in (OP_SIN, OP_COS, OP_TAN)

    t = node[0]

    if t == 0:
        return [P(node, standard_radian, (node.op, 0))]

    denoms = [6, 4, 3]

    if node.op != OP_TAN:
        denoms.append(2)

    for i, denominator in enumerate(denoms):
        if is_pi_frac(t, denominator):
            return [P(node, standard_radian, (node.op, i + 1))]

    return []


def standard_radian(root, args):
    op, column = args

    return CONSTANTS[op][column].clone()


MESSAGES[standard_radian] = _('Replace standard radian {0}.')
