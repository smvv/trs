from ..node import ExpressionLeaf as L, OP_MUL, OP_DIV


def gcd(a, b):
    """
    Return greatest common divisor using Euclid's Algorithm.
    """
    while b:
        a, b = b, a % b

    return a


def lcm(a, b):
    """
    Return least common multiple of a and b.
    """
    return a * b // gcd(a, b)


def least_common_multiple(*args):
    """
    Return lcm of args.
    """
    return reduce(lcm, args)


def is_fraction(node, nominator, denominator):
    """
    Check if a node represents the fraction of a given nominator and
    denominator.

    >>> from ..node import ExpressionLeaf as L
    >>> l1, l2, a = L('a'), L(1), L(2)
    >>> is_fraction(a / l2, a, 2)
    True
    >>> is_fraction(l1 / l2 * a, a, 2)
    True
    >>> is_fraction(l2 / l1 * a, a, 2)
    False
    """
    if node.is_op(OP_DIV):
        nom, denom = node

        return nom == nominator and denom == denominator

    if node.is_op(OP_MUL):
        # 1 / denominator * nominator
        # nominator * 1 / denominator
        left, right = node
        fraction = L(1) / denominator

        return (left == nominator and right == fraction) \
               or (right == nominator and left == fraction)

    return False
