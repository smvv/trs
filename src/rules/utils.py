from ..node import ExpressionLeaf as L, OP_MUL, OP_DIV


def greatest_common_divisor(a, b):
    """
    Return greatest common divisor of a and b using Euclid's Algorithm.
    """
    while b:
        a, b = b, a % b

    return a


def lcm(a, b):
    """
    Return least common multiple of a and b.
    """
    return a * b // greatest_common_divisor(a, b)


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


def partition(callback, iterable):
    """
    Partition an iterable into two parts using a callback that returns a
    boolean.

    Example:
    >>> partition(lambda x: x & 1, range(6))
    ([1, 3, 5], [0, 2, 4])
    """
    a, b = [], []

    for item in iterable:
        (a if callback(item) else b).append(item)

    return a, b


def find_variables(node):
    """
    Find all variables in a node.
    """
    if node.is_variable():
        return set([node.value])

    if not node.is_leaf:
        return reduce(lambda a, b: a | b, map(find_variables, node))

    return set()
