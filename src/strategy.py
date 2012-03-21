from rules.sort import move_constant
from rules.numerics import reduce_fraction_constants, fraction_to_int_fraction
from rules.logarithmic import factor_in_exponent_multiplicant


def pick_suggestion(possibilities):
    if not possibilities:
        return

    # TODO: pick the best suggestion.
    for suggestion, p in enumerate(possibilities + [None]):
        if p and p.handler not in [move_constant, fraction_to_int_fraction,
                reduce_fraction_constants, factor_in_exponent_multiplicant]:
            break

    if not p:
        return possibilities[0]

    return possibilities[suggestion]
