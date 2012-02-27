from rules.sort import move_constant
from rules.numerics import reduce_fraction_constants


def pick_suggestion(possibilities):
    if not possibilities:
        return

    # TODO: pick the best suggestion.
    for suggestion, p in enumerate(possibilities + [None]):
        if p and p.handler not in [move_constant, reduce_fraction_constants]:
            break

    if not p:
        return possibilities[0]

    return possibilities[suggestion]
