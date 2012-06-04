# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_MUL, OP_DIV, \
        OP_ADD, OP_POW, OP_SQRT


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


def substitute(f, x, replacement):
    """
    Replace all occurences of variable x in function f with the specified
    replacement.
    """
    if f == x:
        return replacement.clone()

    if f.is_leaf:
        return f

    children = map(lambda c: substitute(c, x, replacement), f)

    return N(f.op, *children, negated=f.negated)


def divides(m, n):
    """
    Check if m | n (m divides n).
    """
    return not divmod(n, m)[1]


def dividers(n):
    """
    Find all integers that divide n, except for 1.
    """
    def m_dividers(m):
        result, rest = divmod(n, m)

        if not rest:
            return [m, result] if m != result else [m]

    below_sqrt = filter(None, map(m_dividers, xrange(2, int(n ** .5) + 1)))
    div = reduce(lambda a, b: a + b, below_sqrt, [])
    div.sort()

    return div


def is_prime(n):
    """
    Check if n is a prime.
    """
    if n == 2:
        return True

    if n < 2 or not n & 1:
        return False

    for i in xrange(3, int(n ** .5) + 1, 2):
        if not divmod(n, i)[1]:
            return False

    return True


def prime_dividers(n):
    """
    Find all primes that divide n.
    """
    return filter(is_prime, dividers(n))


def is_numeric_node(node):
    """
    Check if a node is numeric.
    """
    return node.is_numeric()


def evals_to_numeric(node):
    """
    Check if a node will eventually evaluate to a numeric value, by checking if
    all leaves are numeric and there are only operators that can be
    considerered a constant or will evaluate to one (+, *, /, ^, sqrt).
    """
    if node.is_leaf:
        return node.is_numeric()

    return node.op in (OP_ADD, OP_MUL, OP_DIV, OP_POW, OP_SQRT) \
           and all(map(evals_to_numeric, node))


def iter_pairs(list_iterable):
    """
    Iterate over a list iterable in left-right pairs.
    """
    if len(list_iterable) < 2:
        raise StopIteration

    for i, left in enumerate(list_iterable[:-1]):
        yield left, list_iterable[i + 1]


def range_except(start, end, exception):
    return range(start, exception) + range(exception + 1, end)
