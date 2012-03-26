from .utils import find_variables, first_sorted_variable, infinity, \
        replace_variable
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


#def integral_params(integral):
#    """
#    Get integral parameters:
#    - If f(x) and x are both specified, return them.
#    - If only f(x) is specified, find x.
#    """
#    if len(integral) > 1:
#        assert integral[1].is_identifier()
#        return tuple(integral[:2])
#
#    f = integral[0]
#    variables = find_variables(integral)
#
#    if not len(variables):
#        return f, None
#
#    return f, L(first_sorted_variable(variables))


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
    - If only a lower bound is specified, set the upper bound to infinity.
    - Given a lower bound a and upper bound b, the solution is F(b) - F(a).
    """
    F += choose_constant(integral)

    if len(integral) < 3:
        return F

    x = integral[1]
    lower = integral[2]
    upper = infinity() if len(integral) < 4 else integral[3]

    # TODO: add notation [F(x)]_a^b
    return replace_variable(F, x, lower) - replace_variable(F, x, upper)


def match_integrate_variable_power(node):
    """
    int x ^ n dx  ->  x ^ (n + 1) / (n + 1) + c
    int g ^ x dx  ->  g ^ x / ln(g)
    """
    assert node.is_op(OP_INT)

    f, x = node

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
