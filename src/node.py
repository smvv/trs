# vim: set fileencoding=utf-8 :
import os.path
import sys
import copy

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
OP_COMMA = 10
OP_SQRT = 11


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
        'sqrt': OP_SQRT,
        ',': OP_COMMA,
        }


def to_expression(obj):
    return obj if isinstance(obj, ExpressionBase) else ExpressionLeaf(obj)


class ExpressionBase(object):

    def __init__(self, *args, **kwargs):
        self.negated = 0

    def clone(self):
        return copy.deepcopy(self)

    def __lt__(self, other):
        """
        Comparison between this expression{node,leaf} and another
        expression{node,leaf}. This comparison will return True if this
        instance has less value than the other expression{node,leaf}.
        Otherwise, False is returned.

        The comparison is based on the following conditions:

        1. Both are leafs. String comparison of the value is used.
        2. This is a leaf and other is a node. This leaf has less value, thus
           True is returned.
        3. This is a node and other is a leaf. This leaf has more value, thus
           False is returned.
        4. Both are nodes. Compare the polynome properties of the nodes. True
           is returned if this node's root property is less than other's root
           property, or this node's exponent property is less than other's
           exponent property, or this node's coefficient property is less than
           other's coefficient property. Otherwise, False is returned.
        """
        if self.is_leaf:
            if other.is_leaf:
                # Both are leafs, string compare the value.
                return str(self.value) < str(other.value)
            # Self is a leaf, thus has less value than an expression node.
            return True

        if self.is_op(OP_NEG) and self[0].is_leaf:
            if other.is_leaf:
                # Both are leafs, string compare the value.
                return ('-' + str(self.value)) < str(other.value)
            if other.is_op(OP_NEG) and other[0].is_leaf:
                return ('-' + str(self.value)) < ('-' + str(other.value))
            # Self is a leaf, thus has less value than an expression node.
            return True

        if other.is_leaf:
            # Self is an expression node, and the other is a leaf. Thus, other
            # is greater than self.
            return False

        # Both are nodes, compare the polynome properties.
        s_coeff, s_root, s_exp = self.extract_polynome_properties()
        o_coeff, o_root, o_exp = other.extract_polynome_properties()

        return s_root < o_root or s_exp < o_exp or s_coeff < o_coeff

    def is_op(self, op):
        return not self.is_leaf and self.op == op

    def is_op_or_negated(self, op):
        if self.is_leaf:
            return False

        if self.op == OP_NEG:
            return self[0].is_op(op)

        return self.op == op

    def is_leaf_or_negated(self):
        if  self.is_leaf:
            return True

        if self.is_op(OP_NEG):
            return self[0].is_leaf

        return False

    def is_power(self):
        return not self.is_leaf and self.op == OP_POW

    def is_nary(self):
        return not self.is_leaf and self.op in [OP_ADD, OP_SUB, OP_MUL]

    def is_identifier(self):
        return self.type == TYPE_IDENTIFIER

    def is_int(self):
        return self.type == TYPE_INTEGER

    def is_float(self):
        return self.type == TYPE_FLOAT

    def is_numeric(self):
        return self.type & (TYPE_FLOAT | TYPE_INTEGER)

    def __add__(self, other):
        return ExpressionNode('+', self, to_expression(other))

    def __sub__(self, other):
        return ExpressionNode('-', self, to_expression(other))

    def __mul__(self, other):
        return ExpressionNode('*', self, to_expression(other))

    def __div__(self, other):
        return ExpressionNode('/', self, to_expression(other))

    def __pow__(self, other):
        return ExpressionNode('^', self, to_expression(other))

    def __neg__(self):
        self.negated += 1
        return self


class ExpressionNode(Node, ExpressionBase):
    def __init__(self, *args, **kwargs):
        super(ExpressionNode, self).__init__(*args, **kwargs)
        self.type = TYPE_OPERATOR
        self.op = OP_MAP[args[0]]

        if hasattr(self.op, '__call__'):
            self.op = self.op(args)

    def __str__(self):  # pragma: nocover
        return generate_line(self)

    def __eq__(self, other):
        """
        Check strict equivalence.
        """
        if isinstance(other, ExpressionNode):
            return self.op == other.op and self.nodes == other.nodes

        return False

    def substitute(self, old_child, new_child):
        self.nodes[self.nodes.index(old_child)] = new_child

    def graph(self):  # pragma: nocover
        return generate_graph(self)

    def extract_polynome_properties(self):
        """
        Extract polynome properties into tuple format: (coefficient, root,
        exponent). Thus: c * r ^ e will be extracted into the tuple (c, r, e).

        This function will normalize the expression before extracting the
        properties. Therefore, the expression r ^ e * c results the same tuple
        (c, r, e) as the expression c * r ^ e.


        >>> from src.node import ExpressionNode as N, ExpressionLeaf as L
        >>> c, r, e = L('c'), L('r'), L('e')
        >>> n1 = N('*', c, N('^', r, e))
        >>> n1.extract_polynome()
        (c, r, e)
        >>> n2 = N('*', N('^', r, e), c)
        >>> n2.extract_polynome()
        (c, r, e)
        >>> n3 = N('-', r)
        >>> n3.extract_polynome()
        (1, -r, 1)
        """
        # TODO: change "get_polynome" -> "extract_polynome".
        # TODO: change retval of c * r ^ e to (c, r, e).
        # was: (root, exponent, coefficient, literal_exponent)

        # rule: r ^ e -> (1, r, e)
        if self.is_power():
            return (ExpressionLeaf(1), self[0], self[1])

        # rule: -r -> (1, r, 1)
        if self.is_op(OP_NEG):
            return (ExpressionLeaf(1), -self[0], ExpressionLeaf(1))

        if self.op != OP_MUL:
            return

        # rule: 3 * 7 ^ e | 'a' * 'b' ^ e

        # expression: c * r ^ e ; tree:
        #
        #    *
        #   ╭┴───╮
        #   c    ^
        #      ╭─┴╮
        #      r  e
        #
        # rule: c * r ^ e | (r ^ e) * c
        for i, j in ((0, 1), (1, 0)):
            if self[j].is_power():
                return (self[i], self[j][0], self[j][1])

        # Normalize c * r and r * c -> c * r. Otherwise, the tuple will not
        # match if the order of the expression is different. Example:
        #   r ^ e * c == c * r ^ e
        # without normalization, those expressions will not match.
        #
        # rule: c * r | r * c
        if self[0] < self[1]:
            return (self[0], self[1], ExpressionLeaf(1))
        return (self[1], self[0], ExpressionLeaf(1))

    def equals(self, other):
        """
        Perform a non-strict equivalence check between two nodes:
        - If the other node is a leaf, it cannot be equal to this node.
        - If their operators differ, the nodes are not equal.
        - If both nodes are additions or both are multiplications, match each
          node in one scope to one in the other (an injective relationship).
          Any difference in order of the scopes is irrelevant.
        - If both nodes are divisions, the nominator and denominator have to be
          non-strictly equal.
        """
        if not other.is_op(self.op):
            # FIXME: this is if-clause is a problem. To fix this problem
            # permanently, normalize ("x * -1" -> "-1x") before comparing to
            # the other node.

            return False

        if self.op in (OP_ADD, OP_MUL):
            s0 = Scope(self)
            s1 = set(Scope(other))

            # Scopes sould be of equal size
            if len(s0) != len(s1):
                return False

            # Each node in one scope should have an image node in the other
            matched = set()

            for n0 in s0:
                found = False

                for n1 in s1 - matched:
                    if n0.equals(n1):
                        found = True
                        matched.add(n1)
                        break

                if not found:
                    return False
        else:
            # Check if all children are non-strictly equal, preserving order
            for i, child in enumerate(self):
                if not child.equals(other[i]):
                    return False

        return True


class ExpressionLeaf(Leaf, ExpressionBase):
    def __init__(self, *args, **kwargs):
        super(ExpressionLeaf, self).__init__(*args, **kwargs)
        self.type = TYPE_MAP[type(args[0])]

    def __eq__(self, other):
        """
        Check strict equivalence.
        """
        other_type = type(other)

        if other_type in TYPE_MAP:
            return TYPE_MAP[other_type] == self.type and self.value == other

        return other.type == self.type and self.value == other.value

    def equals(self, other):
        """
        Check non-strict equivalence.
        Between leaves, this is the same as strict equivalence.
        """
        return self == other

    def extract_polynome_properties(self):
        """
        An expression leaf will return the polynome tuple (1, r, 1), where r is
        the leaf itself. See also the method extract_polynome_properties in
        ExpressionBase.
        """
        # rule: 1 * r ^ 1 -> (1, r, 1)
        return (ExpressionLeaf(1), self, ExpressionLeaf(1))


class Scope(object):

    def __init__(self, node):
        self.node = node
        self.nodes = get_scope(node)

    def __getitem__(self, key):
        return self.nodes[key]

    def __setitem__(self, key, value):
        self.nodes[key] = value

    def __len__(self):
        return len(self.nodes)

    def __iter__(self):
        return iter(self.nodes)

    def remove(self, node, replacement=None):
        if node.is_leaf:
            node_cmp = hash(node)
        else:
            node_cmp = node

        for i, n in enumerate(self.nodes):
            if n.is_leaf:
                n_cmp = hash(n)
            else:
                n_cmp = n

            if n_cmp == node_cmp:
                if replacement != None:
                    self[i] = replacement
                else:
                    del self.nodes[i]

                return

        raise ValueError('Node "%s" is not in the scope of "%s".'
                         % (node, self.node))

    def as_nary_node(self):
        return nary_node(self.node.value, self.nodes)


def nary_node(operator, scope):
    """
    Create a binary expression tree for an n-ary operator. Takes the operator
    and a list of expression nodes as arguments.
    """
    if len(scope) == 1:
        return scope[0]

    return ExpressionNode(operator, nary_node(operator, scope[:-1]), scope[-1])


def get_scope(node):
    """
    Find all n nodes within the n-ary scope of an operator node.
    """
    scope = []

    for child in node:
        if child.is_op(node.op):
            scope += get_scope(child)
        else:
            scope.append(child)

    return scope
