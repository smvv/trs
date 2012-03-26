from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_MUL, OP_DIV, \
        INFINITY, OP_ABS


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

    >>> a, l1, l2 = L('a'), L(1), L(2)
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


def first_sorted_variable(variables):
    """
    In a set of variables, find the main variable to be used in a derivation or
    integral. The prioritized order is x, y, z, a, b, c, d, ...
    """
    for x in 'xyz':
        if x in variables:
            return x

    return sorted(variables)[0]


def find_variable(exp):
    """
    Find the main (e.g. first prioritized) variable in an expression and return
    it as an ExpressionNode object. If no variable is present, return 'x' by
    default.
    """
    variables = find_variables(exp)

    if not len(variables):
        variables.add('x')

    return L(first_sorted_variable(variables))


def replace_variable(f, x, replacement):
    """
    Replace all occurences of variable x in function f with the specified
    replacement.
    """
    if f == x:
        return replacement.clone()

    if f.is_leaf:
        return f

    children = map(lambda c: replace_variable(c, x, replacement), f)

    return N(f.op, *children)


def infinity():
    """
    Return an infinity leaf node.
    """
    return L(INFINITY)


def absolute(exp):
    """
    Put an 'absolute value' operator on top of the given expression.
    """
    return N(OP_ABS, exp)
