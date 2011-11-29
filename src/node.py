import os.path
import sys

sys.path.insert(0, os.path.realpath('external'))

from graph_drawing.graph import generate_graph


class ExpressionNode(object):
    def __init__(self, operator, *args):
        super(ExpressionNode, self).__init__()
        self.operator, self.args = operator, list(args)

        for a in self.args:
            a.parent = self

    def title(self):
        return self.operator

    def replace(self, node):
        pos = self.parent.args.index(self)
        self.parent.args[pos] = node
        node.parent = self.parent
        self.parent = None

    def __iter__(self):
        return iter(self.args)

    def __len__(self):
        return len(self.args)

    def __getitem__(self, n):
        return self.args[n]

    def __setitem__(self, n, arg):
        self.args[n] = arg

    def __str__(self):
        return generate_graph(self, ExpressionNode)

class ExpressionLeaf(object):
    def __init__(self, value):
        super(ExpressionLeaf, self).__init__()
        self.value = value

    def replace(self, node):
        if not hasattr(self, 'parent'):
            return

        pos = self.parent.args.index(self)
        self.parent.args[pos] = node
        node.parent = self.parent
        self.parent = None

    def title(self):
        return str(self.value)

    def __add__(self, b):
        return self.value + b.value

    def __repr__(self):
        return repr(self.value)

    def __str__(self):
        return str(self.value)

l0 = ExpressionLeaf(3)
l1 = ExpressionLeaf(4)
l2 = ExpressionLeaf(5)
l3 = ExpressionLeaf(7)

n0 = ExpressionNode('+', l0, l1)
n1 = ExpressionNode('+', l2, l3)
n2 = ExpressionNode('*', n0, n1)

print n2

N = ExpressionNode

def rewrite_multiply(node):
    a, b = node[0]
    c, d = node[1]

    ac = N('*', a, c)
    ad = N('*', a, d)
    bc = N('*', b, c)
    bd = N('*', b, d)

    res = N('+', N('+', N('+', ac, ad), bc), bd)

    return res

possibilities = [
        (n0, lambda (x,y): ExpressionLeaf(x + y)),
        (n1, lambda (x,y): ExpressionLeaf(x + y)),
        (n2, rewrite_multiply),
        ]

print '\n--- after rule 2 ---\n'

n_, method = possibilities[2]
new = method(n_)

print new

print '\n--- original graph ---\n'

print n2

print '\n--- apply rule 0 ---\n'

n_, method = possibilities[0]
new = method(n_)
n_.replace(new)

print n2

# Revert rule 0
new.replace(n_)

print '\n--- apply rule 1 ---\n'

n_, method = possibilities[1]
new = method(n_)
n_.replace(new)

print n2
