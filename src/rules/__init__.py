from ..node import OP_ADD, OP_MUL, OP_DIV, OP_POW, OP_NEG, OP_SIN, OP_COS, \
        OP_TAN
from .groups import match_combine_groups
from .factors import match_expand
from .powers import match_add_exponents, match_subtract_exponents, \
        match_multiply_exponents, match_duplicate_exponent, \
        match_raised_fraction, match_remove_negative_exponent, \
        match_exponent_to_root, match_extend_exponent, match_constant_exponent
from .numerics import match_add_numerics, match_divide_numerics, \
        match_multiply_numerics, match_multiply_zero, match_multiply_one, \
        match_raise_numerics
from .fractions import match_constant_division, match_add_constant_fractions, \
        match_expand_and_add_fractions, match_multiply_fractions
from .negation import match_negated_factor, match_negate_polynome, \
        match_negated_division
from .sort import match_sort_multiplicants
from .goniometry import match_add_quadrants, match_negated_parameter, \
        match_half_pi_subtraction, match_standard_radian

RULES = {
        OP_ADD: [match_add_numerics, match_add_constant_fractions,
                 match_combine_groups, match_add_quadrants],
        OP_MUL: [match_multiply_numerics, match_expand, match_add_exponents,
                 match_expand_and_add_fractions, match_multiply_zero,
                 match_negated_factor, match_multiply_one,
                 match_sort_multiplicants, match_multiply_fractions],
        OP_DIV: [match_subtract_exponents, match_divide_numerics,
                 match_constant_division, match_negated_division],
        OP_POW: [match_multiply_exponents, match_duplicate_exponent,
                 match_raised_fraction, match_remove_negative_exponent,
                 match_exponent_to_root, match_extend_exponent,
                 match_constant_exponent, match_raise_numerics],
        OP_NEG: [match_negate_polynome],
        OP_SIN: [match_negated_parameter, match_half_pi_subtraction,
                 match_standard_radian],
        OP_COS: [match_negated_parameter, match_half_pi_subtraction,
                 match_standard_radian],
        OP_TAN: [match_standard_radian],
        }
