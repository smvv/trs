class Possibility(object):
    def __init__(self, root, handler, args):
        self.root = root
        self.handler = handler
        self.args = args

    def __str__(self):
        return '<Possibility root="%s" handler=%s args=%s>' \
                % (self.root, self.handler.func_name, self.args)

    def __repr__(self):
        return str(self)

    # TODO: Add unit tests
    def __eq__(self, other):
        self_arg0, self_arg1 = zip(*self.args)
        other_arg0, other_arg1 = zip(*other.args)

        return self.handler == other.handler \
               and self_arg1 == other_arg1 \
               and map(hash, self_arg0) == map(hash, other_arg0)


def filter_duplicates(items):
    unique = []

    for item in items:
        found = False

        for compare in unique:
            if item == compare:
                found = True
                break

        if not found:
            unique.append(item)

    return unique
