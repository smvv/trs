from itertools import combinations

from node import ExpressionNode as Node, ExpressionLeaf as Leaf
from possibilities import Possibility as P


def match_combine_factors(node):
    """
    n + exp + m -> exp + (n + m)
    k0 * v ^ n + exp + k1 * v ^ n -> exp + (k0 + k1) * v ^ n
    """
    p = []

    if node.is_nary():
        # Collect all nodes that can be combined
        # Numeric leaves
        numerics = []

        # Identifier leaves of all orders, tuple format is;
        # (identifier, exponent, coefficient)
        orders = []

        # Nodes that cannot be combined
        others = []

        for n in node.get_scope():
            if isinstance(n, Leaf):
                if n.is_numeric():
                    numerics.append(n)
                elif n.is_identifier():
                    orders.append((n.value, 1, 1))
            else:
                order = n.get_order()

                if order:
                    orders += order
                else:
                    others.append(n)

        if len(numerics) > 1:
            for num0, num1 in combinations(numerics, 2):
                p.append(P(node, combine_numerics, (num0, num1, others)))

        if len(orders) > 1:
            for order0, order1 in combinations(orders, 2):
                id0, exponent0, coeff0 = order0
                id1, exponent1, coeff1 = order1

                if id0 == id1 and exponent0 == exponent1:
                    # Same identifier and exponent -> combine coefficients
                    args = order0 + (coeff1,) + (others,)
                    p.append(P(node, combine_orders, args))

    return p


def combine_numerics(root, args):
    """
    Combine two numeric leaves in an n-ary plus.

    Example:
    3 + 4 -> 7
    """
    numerics, others = args
    value = sum([n.value for n in numerics])

    return nary_node('+', others + [Leaf(value)])


def combine_orders(root, args):
    """
    Combine two identifier multiplications of any order in an n-ary plus.

    Example:
    3x + 4x -> 7x
    """
    identifier, exponent, coeff0, coeff1, others = args

    coeff = coeff0 + coeff1

    if not exponent:
        # a ^ 0 -> 1
        ident = Leaf(1)
    elif exponent == 1:
        # a ^ 1 -> a
        ident = Leaf(identifier)
    else:
        # a ^ n -> a ^ n
        ident = Node('^', Leaf(identifier), Leaf(exponent))

    if coeff == 1:
        combined = ident
    else:
        combined = Node('*', Leaf(coeff), ident)

    return nary_node('+', others + [combined])


def nary_node(operator, scope):
    """
    Create a binary expression tree for an n-ary operator. Takes the operator
    and a list of expression nodes as arguments.
    """
    return scope[0] if len(scope) == 1 \
           else Node(operator, nary_node(operator, scope[:-1]), scope[-1])


rules = {
        '+': [match_combine_factors],
        }
