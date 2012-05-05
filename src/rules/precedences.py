from .factors import expand_double, expand_single
from .sort import move_constant
from .numerics import multiply_one, multiply_zero, reduce_fraction_constants, \
        raise_numerics, remove_zero, multiply_numerics, add_numerics
from .logarithmic import factor_in_exponent_multiplicant, \
        factor_out_exponent, raised_base, factor_out_exponent_important
from .derivatives import chain_rule
from .negation import double_negation, negated_factor, negated_nominator, \
        negated_denominator, negated_zero
from .factors import expand_double, expand_single
from .fractions import multiply_with_fraction, divide_fraction_by_term, \
        add_nominators
from .integrals import factor_out_constant, integrate_variable_root
from .powers import remove_power_of_one
from .sqrt import quadrant_sqrt, extract_sqrt_mult_priority
from .lineq import substitute_variable, swap_sides, divide_term, multiply_term


# Functions to move to the beginning of the possibilities list. Pairs of within
# the list itself are compared by their position in the list: lower in the list
# means lower priority
HIGH = [
        raised_base,

        # 4 / 4 + 1 / 4 -> 5 / 4 instead of 1 + 1/4
        add_nominators,
        ]


# Functions to move to the end of the possibilities list. Pairs of within the
# list itself are compared by their position in the list: lower in the list
# means lower priority
LOW = [
        factor_in_exponent_multiplicant,
        reduce_fraction_constants,

        # Sorting expression terms has a low priority because it is assumed to
        # be handled by the user
        move_constant,
        ]


# Fucntion precedences relative to eachother. Tuple (A, B) means that A has a
# higher priority than B. This list ignores occurences in the HIGH or LOW lists
# above
RELATIVE = [
        # Precedences needed for 'power rule' (derivative of an exponentiation)
        (chain_rule, raised_base),
        (raised_base, factor_out_exponent),

        # Expand 'single' before 'double' to avoid unnessecary complexity
        (expand_single, expand_double),

        (factor_out_exponent_important, raise_numerics),

        (factor_out_constant, multiply_with_fraction),

        # int x dx  ->  int x ^ 1 dx  # do not remove power of one that has
        #                             # deliberately been inserted
        (integrate_variable_root, remove_power_of_one),

        # When simplifying square roots, bring numeric quadrants out of the
        # root first
        (extract_sqrt_mult_priority, multiply_numerics),

        # sqrt(2 ^ 2)  ->  2  # rather than sqrt(4)
        (quadrant_sqrt, raise_numerics),

        # Prevent cycles that are caused by multiplication reductions when
        # splitting up fractions
        (divide_fraction_by_term, multiply_numerics),

        # Prevent useless swapping when solving multiple equations
        (substitute_variable, swap_sides),

        # When solving of an equation with constants, expanding an equation has
        # a lower priority
        (divide_term, multiply_term, swap_sides, expand_double, expand_single),
        ]


# Convert to dictionaries for efficient lookup
HIGH = dict([(h, i) for i, h in enumerate(HIGH)])
LOW = dict([(h, i) for i, h in enumerate(LOW)])


# List of implicit rules. Implicit rules are considered trivial and are
# therefore not printed in verbose rewrite_all mode
IMPLICIT_RULES = [
        negated_factor,
        double_negation,
        negated_nominator,
        negated_denominator,
        multiply_one,
        multiply_zero,
        negated_zero,
        remove_zero,
        remove_power_of_one,
        negated_factor,
        add_numerics,
        ]
