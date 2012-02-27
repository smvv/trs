from rules.sort import move_constant


def pick_suggestion(possibilities):
    if not possibilities:
        return

    # TODO: pick the best suggestion.
    for suggestion, p in enumerate(possibilities + [None]):
        if p and p.handler not in [move_constant]:
            break

    if not p:
        return possibilities[0]

    return possibilities[suggestion]


