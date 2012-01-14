from ..node import ExpressionLeaf as L, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_constant_division(node):
    """
    a / 0  ->  Division by zero
    a / 1  ->  a
    0 / a  ->  0
    """
    assert node.is_op(OP_DIV)

    p = []
    nominator, denominator = node

    # a / 0
    if denominator == 0:
        raise ZeroDivisionError()

    # a / 1
    if denominator == 1:
        p.append(P(node, division_by_one, (nominator,)))

    # 0 / a
    if nominator == 0:
        p.append(P(node, division_of_zero))

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
