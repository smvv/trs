from ..node import OP_ADD, OP_MUL, OP_DIV, OP_POW, OP_NEG, OP_SIN, OP_COS, \
        OP_TAN, OP_DER, OP_LOG, OP_INT, OP_INT_INDEF, OP_EQ, OP_ABS, OP_SQRT, \
        OP_AND, OP_OR
from .groups import match_combine_groups
from .factors import match_expand
from .powers import match_add_exponents, match_subtract_exponents, \
        match_multiply_exponents, match_duplicate_exponent, \
        match_raised_fraction, match_remove_negative_exponent, \
        match_exponent_to_root, match_extend_exponent, match_constant_exponent
from .numerics import match_add_numerics, match_divide_numerics, \
        match_multiply_numerics, match_multiply_zero, match_raise_numerics
from .fractions import match_constant_division, match_add_fractions, \
        match_multiply_fractions, match_divide_fractions, \
        match_extract_fraction_terms, match_division_in_denominator
from .negation import match_negated_factor, match_negate_polynome, \
        match_negated_division
from .sort import match_sort_polynome, match_sort_monomial
from .goniometry import match_add_quadrants, match_negated_parameter, \
        match_half_pi_subtraction, match_standard_radian
from .derivatives import match_zero_derivative, \
        match_one_derivative, match_variable_power, \
        match_const_deriv_multiplication, match_logarithmic, \
        match_goniometric, match_sum_product_rule, match_quotient_rule
from .logarithmic import match_constant_logarithm, \
        match_add_logarithms, match_raised_base, match_factor_out_exponent, \
        match_factor_in_multiplicant, match_expand_terms
from .integrals import match_solve_indef, match_constant_integral, \
        match_integrate_variable_power, match_factor_out_constant, \
        match_division_integral, match_function_integral, \
        match_sum_rule_integral, match_remove_indef_constant
from .lineq import match_move_term, match_multiple_equations, match_double_case
from .absolute import match_factor_out_abs_term
from .sqrt import match_reduce_sqrt


RULES = {
        OP_ADD: [match_add_numerics, match_add_fractions,
                 match_combine_groups, match_add_quadrants,
                 match_add_logarithms, match_sort_polynome],
        OP_MUL: [match_multiply_numerics, match_expand, match_add_exponents,
                 match_multiply_zero, match_negated_factor,
                 match_multiply_fractions, match_factor_in_multiplicant,
                 match_sort_monomial],
        OP_DIV: [match_subtract_exponents, match_divide_numerics,
                 match_constant_division, match_divide_fractions,
                 match_negated_division, match_extract_fraction_terms,
                 match_division_in_denominator],
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
        OP_LOG: [match_constant_logarithm, match_factor_out_exponent,
                 match_expand_terms],
        OP_INT: [match_integrate_variable_power, match_constant_integral,
                 match_factor_out_constant, match_division_integral,
                 match_function_integral, match_sum_rule_integral],
        OP_INT_INDEF: [match_remove_indef_constant, match_solve_indef],
        OP_EQ: [match_move_term],
        OP_ABS: [match_factor_out_abs_term],
        OP_SQRT: [match_reduce_sqrt],
        OP_AND: [match_multiple_equations, match_double_case],
        OP_OR: [match_double_case],
        }
