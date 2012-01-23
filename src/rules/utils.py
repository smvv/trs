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
