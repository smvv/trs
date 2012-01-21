# Each rule will append its hint message to the following dictionary. The
# function pointer to the apply function of the rule is used as key. The
# corresponding value is a string, which will be used to produce the hint
# message. The string will be processed using string.format().
MESSAGES = {}


class Possibility(object):
    def __init__(self, root, handler, args=()):
        self.root = root
        self.handler = handler
        self.args = args

    def __str__(self):
        if self.handler in MESSAGES:
            return MESSAGES[self.handler].format(self.root, *self.args)

        return '<Possibility root="%s" handler=%s args=%s>' \
                % (self.root, self.handler.func_name, self.args)

    def __repr__(self):
        return '<Possibility root="%s" handler=%s args=%s>' \
                % (self.root, self.handler.func_name, self.args)

    def __eq__(self, other):
        return self.handler == other.handler \
               and hash(self.root) == hash(other.root) \
               and self.args == other.args


def filter_duplicates(possibilities):
    """
    Filter duplicated possibilities. Duplicated possibilities occur in n-ary
    nodes, the root-level node and a lower-level node will both recognize a
    rewrite possibility within their scope, whereas only the root-level one
    matters.

    Example: 1 + 2 + 3
    The addition of 1 and 2 is recognized by n-ary additions "1 + 2" and
    "1 + 2 + 3". The "1 + 2" addition should be removed by this function.
    """
    features = []
    unique = []

    for p in reversed(possibilities):
        feature = (p.handler, p.args)

        if feature not in features:
            features.append(feature)
            unique.insert(0, p)

    return unique


def pick_suggestion(possibilities):
    # TODO: pick the best suggestion.
    suggestion = 0
    return possibilities[suggestion]


def apply_suggestion(suggestion):
    return suggestion.handler(suggestion.root, suggestion.args)
