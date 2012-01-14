from ..node import ExpressionNode as Node


def nary_node(operator, scope):
    """
    Create a binary expression tree for an n-ary operator. Takes the operator
    and a list of expression nodes as arguments.
    """
    return scope[0] if len(scope) == 1 \
           else Node(operator, nary_node(operator, scope[:-1]), scope[-1])


def is_prime(n):
    """
    Check if the given integer n is a prime number.
    """
    if n == 2:
        return True

    if n < 2 or not n & 1:
        return False

    for i in xrange(3, int(n ** .5) + 1, 2):
        if not divmod(n, i)[1]:
            return False

    return True


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
