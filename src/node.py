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

OP_MAP = {
        '+': OP_ADD,
        # Either substraction or negation. Skip the operator sign in 'x' (= 2).
        '-': lambda x: OP_SUB if len(x) > 2 else OP_NEG,
        '*': OP_MUL,
        '/': OP_DIV,
        '^': OP_POW,
        'mod': OP_MOD,
        'int': OP_INT,
        'expand': OP_EXPAND,
        }


class ExpressionBase(object):
    def is_leaf(self):
        return self.type != TYPE_OPERATOR

    def is_power(self):
        return not self.is_leaf() and self.op == OP_POW

    def is_nary(self):
        return not self.is_leaf() and self.op in [OP_ADD, OP_SUB, OP_MUL]

    def is_identifier(self):
        return self.is_leaf() and self.type & TYPE_IDENTIFIER

    def is_int(self):
        return self.is_leaf() and self.type & TYPE_INTEGER

    def is_float(self):
        return self.is_leaf() and self.type & TYPE_FLOAT

    def is_numeric(self):
        return self.is_leaf() and self.type & (TYPE_FLOAT | TYPE_INTEGER)


class ExpressionNode(Node, ExpressionBase):
    def __init__(self, *args, **kwargs):
        super(ExpressionNode, self).__init__(*args, **kwargs)
        self.type = TYPE_OPERATOR
        self.op = OP_MAP[args[0]]

        if hasattr(self.op, '__call__'):
            self.op = self.op(args)

    def __str__(self):  # pragma: nocover
        return generate_line(self)

    def graph(self):  # pragma: nocover
        return generate_graph(self)

    def replace(self, node):
        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None

    def get_polynome(self):
        """
        Identifier nodes of all polynomes, tuple format is:
        (identifier, exponent, coefficient, literal_exponent)
        """
        if self.is_power():
            # a ^ e
            return (self[0], self[1], ExpressionLeaf(1), True)

        if self.op != OP_MUL:
            return

        for n0, n1 in [(0, 1), (1, 0)]:
            if self[n0].is_numeric():
                if self[n1].is_identifier():
                    # c * a
                    return (self[n1], ExpressionLeaf(1), self[n0], False)
                elif self[n1].is_power():
                    # c * a ^ e
                    coeff, power = self
                    root, exponent = power

                    return (root, exponent, coeff, True)

    def get_scope(self):
        """"""
        scope = []
        #op = OP_ADD | OP_SUB if self.op & (OP_ADD | OP_SUB) else self.op

        for child in self:
            if not child.is_leaf() and child.op == self.op:
                scope += child.get_scope()
            else:
                scope.append(child)

        return scope


class ExpressionLeaf(Leaf, ExpressionBase):
    def __init__(self, *args, **kwargs):
        super(ExpressionLeaf, self).__init__(*args, **kwargs)

        self.type = TYPE_MAP[type(args[0])]

    def get_polynome(self):
        """
        Identifier nodes of all polynomes, tuple format is:
        (identifier, exponent, coefficient, literal_exponent)
        """
        # a = 1 * a ^ 1
        return (self, ExpressionLeaf(1), ExpressionLeaf(1), False)

    def replace(self, node):
        if not hasattr(self, 'parent'):
            return

        pos = self.parent.nodes.index(self)
        self.parent.nodes[pos] = node
        node.parent = self.parent
        self.parent = None
