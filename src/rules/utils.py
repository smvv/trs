from ..node import ExpressionNode as Node


def nary_node(operator, scope):
    """
    Create a binary expression tree for an n-ary operator. Takes the operator
    and a list of expression nodes as arguments.
    """
    return scope[0] if len(scope) == 1 \
           else Node(operator, nary_node(operator, scope[:-1]), scope[-1])


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
