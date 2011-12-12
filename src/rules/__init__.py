from ..node import OP_ADD, OP_MUL
from .poly import match_combine_factors, match_expand


RULES = {
        OP_ADD: [match_combine_factors],
        OP_MUL: [match_expand],
        }
