# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
from .factors import expand_double, expand_single
from .sort import swap_factors
from .numerics import multiply_one, multiply_zero, reduce_fraction_constants, \
        raise_numerics, remove_zero, multiply_numerics, add_numerics
from .logarithmic import factor_in_exponent_multiplicant, \
        factor_out_exponent, raised_base, factor_out_exponent_important
from .derivatives import chain_rule
from .negation import double_negation, negated_factor, negated_nominator, \
        negated_denominator, negated_zero
from .fractions import multiply_with_fraction, divide_fraction_by_term, \
        add_nominators, division_by_one
from .integrals import factor_out_constant, integrate_variable_root
from .powers import remove_power_of_one, extend_exponent
from .sqrt import quadrant_sqrt, extract_sqrt_mult_priority
from .lineq import substitute_variable, swap_sides, divide_term, multiply_term
from .groups import combine_groups


# Functions to move to the beginning of the possibilities list. Pairs of within
# the list itself are compared by their position in the list: lower in the list
# means lower priority
HIGH = [
        raised_base,

        # 4 / 4 + 1 / 4 -> 5 / 4 instead of 1 + 1/4
        add_nominators,

        # Some operations are obvious, they are mostly done on-the-fly
        multiply_zero,
        multiply_one,
        remove_zero,
        double_negation,
        division_by_one,
        add_numerics,
        multiply_numerics,
        negated_factor,

        # Combine occurences before doing other stuff to prevent duplicate
        # calculations
        combine_groups,
        ]


# Functions to move to the end of the possibilities list. Pairs of within the
# list itself are compared by their position in the list: lower in the list
# means lower priority
LOW = [
        factor_in_exponent_multiplicant,
        reduce_fraction_constants,

        # These rules lead to a longer expression, and are therefore not
        # preferred as a first step
        # Expand 'single' before 'double' to avoid unnessecary complexity
        extend_exponent,
        expand_single,
        expand_double,

        # Sorting expression terms has a low priority because it is assumed to
        # be handled by the user
        swap_factors,
        ]


# Function precedences relative to eachother. Tuple (A, B) means that A has a
# higher priority than B. This list ignores occurences in the HIGH or LOW lists
# above
RELATIVE = [
        # Precedences needed for 'power rule' (derivative of an exponentiation)
        (chain_rule, raised_base),
        (raised_base, factor_out_exponent),

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
        (divide_term, multiply_term, swap_sides),
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
        multiply_zero,
        multiply_one,
        division_by_one,
        negated_zero,
        remove_zero,
        remove_power_of_one,
        add_numerics,
        swap_factors,
        ]
