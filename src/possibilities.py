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

    def __eq__(self, other):
        return self.handler == other.handler \
               and map(hash, self.args) == map(hash, other.args)


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
