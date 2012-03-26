from .utils import find_variables, infinity, replace_variable, find_variable
from .logarithmic import ln
#from .goniometry import sin, cos
from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_INT, \
        OP_INT_INDEF
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def integral(*args):
    """
    Create an integral node.
    """
    return N(OP_INT, *args)


def indef(*args):
    """
    Create an indefinite integral node.
    """
    return N(OP_INT_INDEF, *args)


def choose_constant(integral):
    """
    Choose a constant to be added to the antiderivative.
    """
    # TODO: comments
    occupied = find_variables(integral)
    c = 'c'
    i = 96

    while c in occupied:
        i += 2 if i == 98 else 1
        c = chr(i)

    return L(c)


def solve_integral(integral, F):
    """
    Solve an integral given its anti-derivative F:
    - First, finish the anti-derivative by adding a constant.
    - If no bounds are specified, return the anti-derivative.
    - Given a lower bound a and upper bound b, the solution is the indefinite
      integral [F(x)]_a^b. If F(x) contains multiple variables so that the 'x'
      is not identified by 'find_variable(F)' (which is used by the indefinite
      integral), skip the reduction of the indefinite integral and return the
      solution F(b) - F(a).
    """
    F += choose_constant(integral)

    if len(integral) < 3:
        return F

    x, lbnd, ubnd = integral[1:4]

    if x != find_variable(F):
        return replace_variable(F, x, ubnd) - replace_variable(F, x, lbnd)

    return indef(F, lbnd, ubnd)


def match_solve_indef(node):
    """
    [F(x)]_a^b  ->  F(b) - F(a)
    """
    assert node.is_op(OP_INT_INDEF)

    return [P(node, solve_indef)]


def solve_indef(root, args):
    """
    [F(x)]_a^b  ->  F(b) - F(a)
    """
    Fx, a, b = root
    x = find_variable(Fx)

    return replace_variable(Fx, x, b) - replace_variable(Fx, x, a)


def match_integrate_variable_power(node):
    """
    int x ^ n dx  ->  x ^ (n + 1) / (n + 1) + c
    int g ^ x dx  ->  g ^ x / ln(g)
    """
    assert node.is_op(OP_INT)

    f, x = node[:2]

    if f.is_power():
        root, exponent = f

        if root == x and not exponent.contains(x):
            return [P(node, integrate_variable_root)]

        if exponent == x and not root.contains(x):
            return [P(node, integrate_variable_exponent)]

    return []


def integrate_variable_root(root, args):
    """
    int x ^ n dx  ->  x ^ (n + 1) / (n + 1) + c
    """
    x, n = root[0]

    return solve_integral(root, x ** (n + 1) / (n + 1))


MESSAGES[integrate_variable_root] = \
        _('Apply standard integral int(x ^ n) = x ^ (n + 1) / (n + 1) + c.')


def integrate_variable_exponent(root, args):
    """
    int g ^ x dx  ->  g ^ x / ln(g)
    """
    g, x = root[0]

    return solve_integral(root, g ** x / ln(g))


MESSAGES[integrate_variable_exponent] = \
        _('Apply standard integral int(g ^ x) = g ^ x / ln(g) + c.')
