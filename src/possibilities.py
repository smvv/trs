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

        return self.__repr__()

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
    if not possibilities:
        return

    # TODO: pick the best suggestion.
    suggestion = 0
    return possibilities[suggestion]


def apply_suggestion(root, subtree_map, suggestion):
    # clone the root node before modifying. After deep copying the root node,
    # the subtree_map cannot be used since the hash() of each node in the deep
    # copied root node has changed.
    #root_clone = root.clone()

    subtree = suggestion.handler(suggestion.root, suggestion.args)

    if suggestion.root in subtree_map:
        parent_node = subtree_map[suggestion.root]
    else:
        parent_node = None

    # There is either a parent node or the subtree is the root node.
    # FIXME: FAIL: test_diagnostic_test_application in tests/test_b1_ch08.py
    #try:
    #    assert bool(parent_node) != (subtree == root)
    #except:
    #    print 'parent_node: %s' % (str(parent_node))
    #    print 'subtree: %s == %s' % (str(subtree), str(root))
    #    raise

    if parent_node:
        parent_node.substitute(suggestion.root, subtree)
        return root
    return subtree
