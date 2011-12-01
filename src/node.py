import os.path
import sys

sys.path.insert(0, os.path.realpath('external'))

from graph_drawing.graph import generate_graph
from graph_drawing.line import generate_line
from graph_drawing.node import Node, Leaf


#NODE_TYPE = 0
#NODE_

class ExpressionNode(Node):
    def __init__(self, *args, **kwargs):
        super(ExpressionNode, self).__init__(*args, **kwargs)
        #self.type = NODE_TYPE

    def __str__(self):
        return generate_line(self)

    def replace(self, node):
        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None

    def graph(self):
        return generate_graph(self)

class ExpressionLeaf(Leaf):
    def replace(self, node):
        if not hasattr(self, 'parent'):
            return

        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None


if __name__ == '__main__':
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
            (n0, lambda (x,y): ExpressionLeaf(x.value + y.value)),
            (n1, lambda (x,y): ExpressionLeaf(x.value + y.value)),
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
