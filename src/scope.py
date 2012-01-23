from rules.utils import nary_node


class Scope(object):

    def __init__(self, node):
        self.node = node
        self.nodes = node.get_scope()

    def remove(self, node, replacement=None):
        if node.is_leaf():
            node_cmp = hash(node)
        else:
            node_cmp = node

        for i, n in enumerate(self.nodes):
            if n.is_leaf():
                n_cmp = hash(n)
            else:
                n_cmp = n

            if n_cmp == node_cmp:
                if replacement != None:
                    self.nodes[i] = replacement
                else:
                    del self.nodes[i]

                return

        raise ValueError('Node "%s" is not in the scope of "%s".'
                         % (node, self.node))

    def as_nary_node(self):
        return nary_node(self.node.value, self.nodes)
