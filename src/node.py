# vim: set fileencoding=utf-8 :
import os.path
import sys
import copy
import re

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
OP_ABS = 2

# Binary
OP_ADD = 3
OP_SUB = 4
OP_MUL = 5
OP_DIV = 6
OP_POW = 7
OP_SUBSCRIPT = 8
OP_AND = 9
OP_OR = 10

# N-ary (functions)
OP_INT = 11
OP_INT_INDEF = 12
OP_COMMA = 13
OP_SQRT = 14
OP_DER = 15
OP_LOG = 16

# Goniometry
OP_SIN = 17
OP_COS = 18
OP_TAN = 19

OP_SOLVE = 20
OP_EQ = 21

OP_POSSIBILITIES = 22
OP_HINT = 23
OP_REWRITE_ALL = 24
OP_REWRITE_ALL_VERBOSE = 25
OP_REWRITE = 26

# Special identifiers
PI = 'pi'
E = 'e'
INFINITY = 'oo'

SPECIAL_TOKENS = [PI, E, INFINITY]

# Default base to use in parsing 'log(...)'
DEFAULT_LOGARITHM_BASE = 10


TYPE_MAP = {
        int: TYPE_INTEGER,
        float: TYPE_FLOAT,
        str: TYPE_IDENTIFIER,
        }

OP_MAP = {
        ',': OP_COMMA,
        '+': OP_ADD,
        '-': OP_SUB,
        '*': OP_MUL,
        '/': OP_DIV,
        '^': OP_POW,
        '_': OP_SUBSCRIPT,
        '^^': OP_AND,
        'vv': OP_OR,
        'sin': OP_SIN,
        'cos': OP_COS,
        'tan': OP_TAN,
        'sqrt': OP_SQRT,
        'int': OP_INT,
        'der': OP_DER,
        'solve': OP_SOLVE,
        'log': OP_LOG,
        '=': OP_EQ,
        '??': OP_POSSIBILITIES,
        '?': OP_HINT,
        '@': OP_REWRITE,
        '@@': OP_REWRITE_ALL,
        '@@@': OP_REWRITE_ALL_VERBOSE,
        }

OP_VALUE_MAP = dict([(v, k) for k, v in OP_MAP.iteritems()])
OP_MAP['ln'] = OP_LOG
OP_VALUE_MAP[OP_INT_INDEF] = 'indef'
OP_VALUE_MAP[OP_ABS] = 'abs'

TOKEN_MAP = {
        OP_COMMA: 'COMMA',
        OP_ADD: 'PLUS',
        OP_SUB: 'MINUS',
        OP_MUL: 'TIMES',
        OP_DIV: 'DIVIDE',
        OP_POW: 'POW',
        OP_SUBSCRIPT: 'SUB',
        OP_AND: 'AND',
        OP_OR: 'OR',
        OP_SQRT: 'FUNCTION',
        OP_SIN: 'FUNCTION',
        OP_COS: 'FUNCTION',
        OP_TAN: 'FUNCTION',
        OP_INT: 'INTEGRAL',
        OP_DER: 'FUNCTION',
        OP_SOLVE: 'FUNCTION',
        OP_LOG: 'FUNCTION',
        OP_EQ: 'EQ',
        OP_POSSIBILITIES: 'POSSIBILITIES',
        OP_HINT: 'HINT',
        OP_REWRITE: 'REWRITE',
        OP_REWRITE_ALL: 'REWRITE_ALL',
        OP_REWRITE_ALL_VERBOSE: 'REWRITE_ALL_VERBOSE',
        }


def to_expression(obj):
    if isinstance(obj, ExpressionBase):
        return obj.clone()

    return ExpressionLeaf(obj)


class ExpressionBase(object):
    def __init__(self, *args, **kwargs):
        self.negated = 0

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
                self_value = '-' * (self.negated & 1) + str(self.value)
                other_value = '-' * (other.negated & 1) + str(other.value)

                return self_value < other_value

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

    def __ne__(self, other):
        """
        Check strict inequivalence, using the strict equivalence operator.
        """
        return not (self == other)

    def clone(self):
        return copy.deepcopy(self)

    def is_op(self, *ops):
        return not self.is_leaf and self.op in ops

    def is_power(self, exponent=None):
        if self.is_leaf or self.op != OP_POW:
            return False

        return exponent == None or self[1] == exponent

    def is_nary(self):
        return not self.is_leaf and self.op in [OP_ADD, OP_SUB, OP_MUL]

    def is_identifier(self, identifier=None):
        return self.type == TYPE_IDENTIFIER \
               and (identifier == None or self.value == identifier)

    def is_variable(self):
        return self.type == TYPE_IDENTIFIER and self.value not in (PI, E)

    def is_int(self):
        return self.type == TYPE_INTEGER

    def is_float(self):
        return self.type == TYPE_FLOAT

    def is_numeric(self):
        return self.type & (TYPE_FLOAT | TYPE_INTEGER)

    def __add__(self, other):
        return ExpressionNode(OP_ADD, self, to_expression(other))

    def __sub__(self, other):
        return ExpressionNode(OP_ADD, self, -to_expression(other))
        #FIXME: return ExpressionNode(OP_SUB, self, to_expression(other))

    def __mul__(self, other):
        return ExpressionNode(OP_MUL, self, to_expression(other))

    def __div__(self, other):
        return ExpressionNode(OP_DIV, self, to_expression(other))

    def __pow__(self, other):
        return ExpressionNode(OP_POW, self, to_expression(other))

    def __pos__(self):
        return self.reduce_negation()

    def __and__(self, other):
        return ExpressionNode(OP_AND, self, to_expression(other))

    def __or__(self, other):
        return ExpressionNode(OP_OR, self, to_expression(other))

    def reduce_negation(self, n=1):
        """Remove n negation flags from the node."""
        assert self.negated >= n

        return self.negate(-n)

    def negate(self, n=1):
        """Negate the node n times."""
        return negate(self, self.negated + n)

    def contains(self, node, include_self=True):
        """
        Check if a node equal to the specified one exists within this node.
        """
        if include_self and negate(self, 0) == node:
            return True

        if not self.is_leaf:
            for child in self:
                if child.contains(node, include_self=True):
                    return True

        return False


class ExpressionNode(Node, ExpressionBase):
    def __init__(self, *args, **kwargs):
        super(ExpressionNode, self).__init__(*args, **kwargs)
        self.type = TYPE_OPERATOR
        op = args[0]

        if isinstance(op, str):
            self.value = op
            self.op = OP_MAP[op]
        else:
            self.value = OP_VALUE_MAP[op]
            self.op = op

    def construct_function(self, children):
        if self.op == OP_DER:
            f = children[0]

            if len(children) < 2:
                # der(der(x ^ 2))  ->  [x ^ 2]''
                if self[0].is_op(OP_DER) and len(self[0]) < 2:
                    return f + '\''

                # der(x ^ 2)  ->  [x ^ 2]'
                return '[' + f + ']\''

            # der(x ^ 2, x)  ->  d/dx (x ^ 2)
            return 'd/d%s (%s)' % (children[1], f)

        if self.op == OP_LOG:
            if self[0].is_op(OP_ABS):
                content = children[0]
            else:
                content = '(' + children[0] + ')'

            # log(a, e)  ->  ln(a)
            if self[1].is_identifier(E):
                return 'ln%s' % content

            # log(a, 10)  ->  log(a)
            if self[1] == 10:
                return 'log%s' % content

            # log(a, 2)  ->  log_2(a)
            if children[1].isdigit():
                return 'log_%s%s' % (children[1], content)

        if self.op == OP_INT:
            # Make sure that any needed parentheses around f(x) are generated,
            # and append ' dx' to it (result 'f(x) dx')
            fx, x = self[:2]
            operand = re.sub(r'(\s*\*)?\s*d$', ' d' + x.value, str(fx * 'd'))
            op = 'int'

            # Add bounds
            if len(self) > 2:
                lbnd, ubnd = self[2:]
                lbnd = str(ExpressionNode(OP_SUBSCRIPT, lbnd))
                ubnd = str(ExpressionNode(OP_POW, ubnd))
                op += lbnd + ubnd

            # int x ^ 2      ->  int x ^ 2 dx
            # int x + 1      ->  int (x + 1) dx
            # int_a^b x ^ 2  ->  int_a^b x ^ 2 dx
            return op + ' ' + operand

        if self.op == OP_INT_INDEF:
            # [x ^ 2]_a^b
            F, lbnd, ubnd = self
            lbnd = str(ExpressionNode(OP_SUBSCRIPT, lbnd))
            ubnd = str(ExpressionNode(OP_POW, ubnd))

            return '[%s]%s%s' % (F, lbnd, ubnd)

        if self.op == OP_ABS:
            return '|%s|' % children[0]

        # Function with absolute value as only parameter does not need
        # parentheses
        if self.op in TOKEN_MAP and TOKEN_MAP[self.op] == 'FUNCTION' \
                and len(self) == 1 and self[0].is_op(OP_ABS):
            return self.title() + children[0]

    def __str__(self):  # pragma: nocover
        return generate_line(self)

    def __eq__(self, other):
        """
        Check strict equivalence.
        """
        return isinstance(other, ExpressionNode) and self.op == other.op \
               and self.negated == other.negated and self.nodes == other.nodes

    def substitute(self, old_child, new_child):
        self.nodes[self.nodes.index(old_child)] = new_child

    def graph(self):  # pragma: nocover
        return generate_graph(negation_to_node(self))

    def extract_polynome_properties(self):
        """
        Extract polynome properties into tuple format: (coefficient, root,
        exponent). Thus: c * r ^ e will be extracted into the tuple (c, r, e).

        This function will normalize the expression before extracting the
        properties. Therefore, the expression r ^ e * c results the same tuple
        (c, r, e) as the expression c * r ^ e.


        >>> from src.node import ExpressionNode as N, ExpressionLeaf as L
        >>> c, r, e = L('c'), L('r'), L('e')
        >>> n1 = N(OP_MUL), c, N('^', r, e))
        >>> n1.extract_polynome()
        (c, r, e)
        >>> n2 = N(OP_MUL, N('^', r, e), c)
        >>> n2.extract_polynome()
        (c, r, e)
        >>> n3 = -r
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
        # rule: --r -> (1, r, 1)
        # rule: ---r -> (1, r, 1)
        if self.negated:
            return (ExpressionLeaf(1), self, ExpressionLeaf(1))

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

    def equals(self, other, ignore_negation=False):
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
        if not isinstance(other, ExpressionNode) or other.op != self.op:
            return False

        if self.op in (OP_ADD, OP_MUL):
            s0 = Scope(self)
            s1 = set(Scope(other))

            # Scopes should be of equal size
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

        if ignore_negation:
            return True

        return self.negated == other.negated


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
            return self.type == TYPE_MAP[other_type] \
                   and self.actual_value() == other

        return self.negated == other.negated and self.type == other.type \
               and self.value == other.value

    def __repr__(self):
        return str(self)

    def equals(self, other, ignore_negation=False):
        """
        Check non-strict equivalence.
        Between leaves, this is the same as strict equivalence, except when
        negations must be ignored.
        """
        if ignore_negation:
            other_type = type(other)

            if other_type in (int, float):
                return TYPE_MAP[other_type] == self.type \
                    and self.value == abs(other)
            elif other_type == str:
                return self.type == TYPE_IDENTIFIER and self.value == other

            return self.type == other.type and self.value == other.value
        else:
            return self == other

    def extract_polynome_properties(self):
        """
        An expression leaf will return the polynome tuple (1, r, 1), where r is
        the leaf itself. See also the method extract_polynome_properties in
        ExpressionBase.
        """
        # rule: 1 * r ^ 1 -> (1, r, 1)
        return (ExpressionLeaf(1), self, ExpressionLeaf(1))

    def actual_value(self):
        if self.type == TYPE_IDENTIFIER:
            return self.value

        return (1 - 2 * (self.negated & 1)) * self.value


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

    def __eq__(self, other):
        return isinstance(other, Scope) and self.node == other.node \
               and self.nodes == other.nodes

    def __repr__(self):
        return '<Scope of "%s">' % repr(self.node)

    def remove(self, node, **kwargs):
        try:
            i = self.nodes.index(node)

            if 'replacement' in kwargs:
                self[i] = kwargs['replacement']
            else:
                del self.nodes[i]
        except ValueError:
            raise ValueError('Node "%s" is not in the scope of "%s".'
                             % (node, self.node))

    def replace(self, node, replacement):
        self.remove(node, replacement=replacement)

    def as_nary_node(self):
        return nary_node(self.node.op, self.nodes).negate(self.node.negated)


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
        if child.is_op(node.op) and not child.negated:
            scope += get_scope(child)
        else:
            scope.append(child)

    return scope


def negate(node, n=1):
    """Negate the given node n times."""
    assert n >= 0

    new_node = node.clone()
    new_node.negated = n

    return new_node


def infinity():
    """
    Return an infinity leaf node.
    """
    return ExpressionLeaf(INFINITY)


def absolute(exp):
    """
    Put an 'absolute value' operator on top of the given expression.
    """
    return ExpressionNode(OP_ABS, exp)


def sin(*args):
    """
    Create a sinus function node.
    """
    return ExpressionNode(OP_SIN, *args)


def cos(*args):
    """
    Create a cosinus function node.
    """
    return ExpressionNode(OP_COS, *args)


def tan(*args):
    """
    Create a tangens function node.
    """
    return ExpressionNode(OP_TAN, *args)


def log(exponent, base=10):
    """
    Create a logarithm function node (default base is 10).
    """
    if not isinstance(base, ExpressionLeaf):
        base = ExpressionLeaf(base)

    return ExpressionNode(OP_LOG, exponent, base)


def ln(exponent):
    """
    Create a natural logarithm node.
    """
    return log(exponent, base=E)


def der(f, x=None):
    """
    Create a derivative node.
    """
    return ExpressionNode(OP_DER, f, x) if x else ExpressionNode(OP_DER, f)


def integral(*args):
    """
    Create an integral node.
    """
    return ExpressionNode(OP_INT, *args)


def indef(*args):
    """
    Create an indefinite integral node.
    """
    return ExpressionNode(OP_INT_INDEF, *args)


def eq(left, right):
    """
    Create an equality operator node.
    """
    return ExpressionNode(OP_EQ, left, right)


def sqrt(exp):
    """
    Create a square root node.
    """
    return ExpressionNode(OP_SQRT, exp)


def negation_to_node(node):
    """
    Recursively replace negation flags inside a node by explicit unary negation
    nodes.
    """
    if node.negated:
        negations = node.negated
        node = negate(node, 0)

        for i in range(negations):
            node = ExpressionNode('-', node)

    if node.is_leaf:
        return node

    return ExpressionNode(node.op, *map(negation_to_node, node))
