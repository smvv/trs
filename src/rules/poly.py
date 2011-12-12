from itertools import combinations

from ..node import ExpressionLeaf as Leaf, TYPE_OPERATOR, OP_ADD
from ..possibilities import Possibility as P


def match_expand(node):
    """
    a * (b + c) -> ab + ac
    """
    if node.type != TYPE_OPERATOR or not node.op & OP_MUL:
        return []

    p = []

    # 'a' parts
    left = []

    # '(b + c)' parts
    right = []

    for n in node.get_scope():
        if node.type == TYPE_OPERATOR:
            if n.op & OP_ADD:
                right.append(n)
        else:
            left.append(n)

    if len(left) and len(right):
        for l in left:
            for r in right:
                p.append(P(node, expand_single, l, r))

    return p

def expand_single(root, args):
    """
    Combine a leaf (left) multiplied with an addition of two expressions
    (right) to an addition of two multiplications.

    >>> a * (b + c) -> a * b + a * c
    """
    left, right = args
    others = list(set(root.get_scope()) - {left, right})

def match_combine_factors(node):
    """
    n + exp + m -> exp + (n + m)
    k0 * v ^ n + exp + k1 * v ^ n -> exp + (k0 + k1) * v ^ n
    """
    if node.type != TYPE_OPERATOR or not node.op & OP_ADD:
        return []

    p = []

    # Collect all nodes that can be combined
    # Numeric leaves
    numerics = []

    # Identifier leaves of all orders, tuple format is;
    # (identifier, exponent, coefficient)
    orders = []

    for n in node.get_scope():
        if node.type == TYPE_OPERATOR:
            order = n.get_order()

            if order:
                orders += order
        else:
            if n.is_numeric():
                numerics.append(n)
            elif n.is_identifier():
                orders.append((n.value, 1, 1))

    if len(numerics) > 1:
        for num0, num1 in combinations(numerics, 2):
            p.append(P(node, combine_numerics, (num0, num1)))

    if len(orders) > 1:
        for order0, order1 in combinations(orders, 2):
            id0, exponent0, coeff0 = order0
            id1, exponent1, coeff1 = order1

            if id0 == id1 and exponent0 == exponent1:
                # Same identifier and exponent -> combine coefficients
                args = order0 + (coeff1,)
                p.append(P(node, combine_orders, args))

    return p


def combine_numerics(root, args):
    """
    Combine two numeric leaves in an n-ary plus.

    Example:
    >>> 3 + 4 -> 7
    """
    others = list(set(root.get_scope()) - set(args))
    value = sum([n.value for n in args])

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
