import os.path
import sys

sys.path.insert(0, os.path.realpath('external'))

from graph_drawing.graph import generate_graph
from graph_drawing.line import generate_line
from graph_drawing.node import Node, Leaf


TYPE_OPERATOR = 1
TYPE_IDENTIFIER = 2
TYPE_INTEGER = 4
TYPE_FLOAT = 8
TYPE_NUMERIC = TYPE_INTEGER | TYPE_FLOAT


# Unary
OP_NEG = 1

# Binary
OP_ADD = 2
OP_SUB = 3
OP_MUL = 4
OP_DIV = 5
OP_POW = 6
OP_MOD = 7

# N-ary (functions)
OP_INT = 8
OP_EXPAND = 9


TYPE_MAP = {
        int: TYPE_INTEGER,
        float: TYPE_FLOAT,
        str: TYPE_IDENTIFIER,
        }


OPT_MAP = {
        '+': OP_ADD,
        '-': OP_SUB,
        '*': OP_MUL,
        '/': OP_DIV,
        '^': OP_POW,
        'mod': OP_MOD,
        'int': OP_INT,
        'expand': OP_EXPAND,
        }


class ExpressionNode(Node):
    def __init__(self, *args, **kwargs):
        super(ExpressionNode, self).__init__(*args, **kwargs)
        self.type = TYPE_OPERATOR
        self.opt = OPT_MAP[args[0]]

    def __str__(self):  # pragma: nocover
        return generate_line(self)

    def graph(self):  # pragma: nocover
        return generate_graph(self)

    def replace(self, node):
        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None

    def is_power(self):
        return self.opt == OP_POW

    def is_nary(self):
        return self.opt in [OP_ADD, OP_SUB, OP_MUL]

    def get_order(self):
        if self.is_power() and self[0].is_identifier() \
                and isinstance(self[1], Leaf):
            return (self[0].value, self[1].value, 1)

        for n0, n1 in [(0, 1), (1, 0)]:
            if self[n0].is_numeric() and not isinstance(self[n1], Leaf) \
                    and self[n1].is_power():
                coeff, power = self

                if power[0].is_identifier() and isinstance(power[1], Leaf):
                    return (power[0].value, power[1].value, coeff.value)

    def get_scope(self):
        scope = []

        for child in self:
            if not isinstance(child, Leaf) and child.opt == self.opt:
                scope += child.get_scope()
            else:
                scope.append(child)

        return scope


class ExpressionLeaf(Leaf):
    def __init__(self, *args, **kwargs):
        super(ExpressionLeaf, self).__init__(*args, **kwargs)

        for data_type, type_repr in TYPE_MAP.iteritems():
            if isinstance(args[0], data_type):
                self.type = type_repr
                break

    def get_order(self):
        if self.is_identifier():
            return (self.value, 1, 1)

    def replace(self, node):
        if not hasattr(self, 'parent'):
            return

        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None

    def is_identifier(self):
        return self.type & TYPE_IDENTIFIER

    def is_int(self):
        return self.type & TYPE_INTEGER

    def is_float(self):
        return self.type & TYPE_FLOAT

    def is_numeric(self):
        return self.type & TYPE_NUMERIC


if __name__ == '__main__':  # pragma: nocover
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
            (n0, lambda (x, y): ExpressionLeaf(x.value + y.value)),
            (n1, lambda (x, y): ExpressionLeaf(x.value + y.value)),
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
