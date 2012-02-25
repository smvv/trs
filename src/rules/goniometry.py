from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, OP_ADD, \
        OP_POW, OP_MUL, OP_SIN, OP_COS, OP_TAN
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
