from ..node import OP_ADD, OP_MUL, OP_DIV, OP_POW, OP_NEG, OP_SIN, OP_COS, \
        OP_TAN, OP_DER, OP_LOG, OP_INT, OP_INT_INDEF, OP_EQ
from .groups import match_combine_groups
from .factors import match_expand
from .powers import match_add_exponents, match_subtract_exponents, \
        match_multiply_exponents, match_duplicate_exponent, \
        match_raised_fraction, match_remove_negative_exponent, \
        match_exponent_to_root, match_extend_exponent, match_constant_exponent
from .numerics import match_add_numerics, match_divide_numerics, \
        match_multiply_numerics, match_multiply_zero, match_multiply_one, \
        match_raise_numerics
from .fractions import match_constant_division, match_add_fractions, \
        match_multiply_fractions, match_divide_fractions, \
        match_equal_fraction_parts
from .negation import match_negated_factor, match_negate_polynome, \
        match_negated_division
from .sort import match_sort_multiplicants
from .goniometry import match_add_quadrants, match_negated_parameter, \
        match_half_pi_subtraction, match_standard_radian
from src.rules.derivatives import match_zero_derivative, \
        match_one_derivative, match_variable_power, \
        match_const_deriv_multiplication, match_logarithmic, \
        match_goniometric, match_sum_product_rule, match_quotient_rule
from src.rules.logarithmic import match_constant_logarithm, \
        match_add_logarithms, match_raised_base, match_factor_out_exponent, \
        match_factor_in_multiplicant
from src.rules.integrals import match_solve_indef, match_constant_integral, \
        match_integrate_variable_power, match_factor_out_constant, \
        match_division_integral, match_function_integral
from src.rules.lineq import match_move_term

RULES = {
        OP_ADD: [match_add_numerics, match_add_fractions,
                 match_combine_groups, match_add_quadrants,
                 match_add_logarithms],
        OP_MUL: [match_multiply_numerics, match_expand, match_add_exponents,
                 match_multiply_zero, match_negated_factor, match_multiply_one,
                 match_sort_multiplicants, match_multiply_fractions,
                 match_factor_in_multiplicant],
        OP_DIV: [match_subtract_exponents, match_divide_numerics,
                 match_constant_division, match_divide_fractions,
                 match_negated_division, match_equal_fraction_parts],
        OP_POW: [match_multiply_exponents, match_duplicate_exponent,
                 match_raised_fraction, match_remove_negative_exponent,
                 match_exponent_to_root, match_extend_exponent,
                 match_constant_exponent, match_raise_numerics,
                 match_raised_base],
        OP_NEG: [match_negate_polynome],
        OP_SIN: [match_negated_parameter, match_half_pi_subtraction,
                 match_standard_radian],
        OP_COS: [match_negated_parameter, match_half_pi_subtraction,
                 match_standard_radian],
        OP_TAN: [match_standard_radian],
        OP_DER: [match_zero_derivative, match_one_derivative,
                 match_variable_power, match_const_deriv_multiplication,
                 match_logarithmic, match_goniometric, match_sum_product_rule,
                 match_quotient_rule],
        OP_LOG: [match_constant_logarithm, match_factor_out_exponent],
        OP_INT: [match_integrate_variable_power, match_constant_integral,
                 match_factor_out_constant, match_division_integral,
                 match_function_integral],
        OP_INT_INDEF: [match_solve_indef],
        OP_EQ: [match_move_term],
        }
