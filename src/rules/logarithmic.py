from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_LOG, OP_LN
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def log(exponent, base=10):
    if not isinstance(base, L):
        base = L(base)

    return N('log', exponent, base)


def ln(exponent):
    return N('ln', exponent)
