from ..node import OP_ADD, OP_MUL
from .poly import match_combine_polynomes, match_expand


RULES = {
        OP_ADD: [match_combine_polynomes],
        OP_MUL: [match_expand],
        }
