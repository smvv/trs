class Possibility(object):
    def __init__(self, root, handler, args):
        self.root = root
        self.handler = handler
        self.args = args

    def __str__(self):
        return '<possibility root="%s" handler=%s args=%s>' \
                % (self.root, self.handler, self.args)

    def __repr__(self):
        return str(self)
