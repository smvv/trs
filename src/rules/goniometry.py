from .utils import is_fraction
from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, OP_ADD, \
        OP_POW, OP_MUL, OP_SIN, OP_COS, OP_TAN, PI
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def sin(*args):
    return N('sin', *args)


def cos(*args):
    return N('cos', *args)


def tan(*args):
    return N('tan', *args)


def match_add_quadrants(node):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    assert node.is_op(OP_ADD)

    p = []
    sin_q, cos_q = node

    if sin_q.is_power(2) and cos_q.is_power(2):
        sin, cos = sin_q[0], cos_q[0]

        if sin.is_op(OP_SIN) and cos.is_op(OP_COS):
            p.append(P(node, add_quadrants, ()))

    return p


def add_quadrants(root, args):
    """
    sin(t) ^ 2 + cos(t) ^ 2  ->  1
    """
    return L(1)


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


def match_standard_radian(node):
    """
    Apply a direct constant calculation from the following table.

        | 0 | pi / 6    | pi / 4    | pi / 3    | pi / 2
    ----+---+-----------+-----------+-----------+-------
    sin | 0 | 1/2       | sqrt(2)/2 | sqrt(3)/2 | 1
    cos | 1 | sqrt(3)/2 | sqrt(2)/2 | 1/2       | 0
    tan | 0 | sqrt(3)/3 | 1         | sqrt(3)   | -
    """
    # TODO: implement
    pass
