from ..node import OP_ADD, OP_MUL, OP_DIV, OP_POW
from .poly import match_combine_polynomes, match_expand
from .powers import match_add_exponents, match_subtract_exponents, \
        match_multiply_exponents, match_duplicate_exponent, \
        match_remove_negative_exponent, match_exponent_to_root
from .numerics import match_divide_numerics
from .fractions import match_constant_division, match_add_constant_fractions, \
        match_expand_and_add_fractions


RULES = {
        OP_ADD: [match_add_constant_fractions, match_combine_polynomes],
        OP_MUL: [match_expand, match_add_exponents, \
                 match_expand_and_add_fractions],
        OP_DIV: [match_subtract_exponents, match_divide_numerics, \
                 match_constant_division],
        OP_POW: [match_multiply_exponents, match_duplicate_exponent, \
                 match_remove_negative_exponent, match_exponent_to_root],
        }
