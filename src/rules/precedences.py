from .factors import expand_double, expand_single
from .sort import move_constant
from .numerics import reduce_fraction_constants
from .logarithmic import factor_in_exponent_multiplicant, \
        factor_out_exponent, raised_base
from .derivatives import chain_rule


# Functions to move to the beginning of the possibilities list. Pairs of within
# the list itself are compared by their position in the list: lower in the list
# means lower priority
HIGH = [
        raised_base,
        ]


# Functions to move to the end of the possibilities list. Pairs of within the
# list itself are compared by their position in the list: lower in the list
# means lower priority
LOW = [
        move_constant,
        reduce_fraction_constants,
        factor_in_exponent_multiplicant,
        ]


# Fucntion precedences relative to eachother. Tuple (A, B) means that A has a
# higer priority than B. This list ignores occurences in the HIGH or LOW lists
# above
RELATIVE = [
        # Precedences needed for 'power rule'
        (chain_rule, raised_base),
        (raised_base, factor_out_exponent),

        # Expand 'single' before 'double' to avoid unnessecary complexity
        (expand_single, expand_double),
        ]


# Convert to dictionaries for efficient lookup
HIGH = dict([(h, i) for i, h in enumerate(HIGH)])
LOW = dict([(h, i) for i, h in enumerate(LOW)])
