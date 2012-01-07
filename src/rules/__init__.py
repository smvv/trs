from ..node import OP_ADD, OP_MUL
from .poly import match_combine_polynomes, match_expand


RULES = {
        OP_ADD: [match_combine_polynomes],
        OP_MUL: [match_expand],
        #OP_MUL: [match_expand, match_add_exponents],
        #OP_DIV: [match_subtract_exponents],
        #OP_POW: [match_multiply_exponents, match_duplicate_exponent, \
        #         match_remove_negative_exponent, match_exponent_to_root],
        }
