from ..node import ExpressionLeaf as L, Scope, OP_ADD, OP_POW, OP_MUL, \
        OP_SIN, OP_COS, OP_TAN
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_add_quadrants(node):
    """
    sin(x) ^ 2 + cos(x) ^ 2  ->  1
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
    sin(x) ^ 2 + cos(x) ^ 2  ->  1
    """
    return L(1)


MESSAGES[add_quadrants] = _('Add the sinus and cosinus quadrants to 1.')
