from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_LOG, E
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def log(exponent, base=10):
    if not isinstance(base, L):
        base = L(base)

    return N(OP_LOG, exponent, base)


def ln(exponent):
    return log(exponent, base=E)
