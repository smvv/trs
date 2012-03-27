from .utils import find_variables, replace_variable, find_variable
from ..node import ExpressionLeaf as L, OP_INT, OP_INT_INDEF, OP_MUL, OP_DIV, \
        OP_LOG, OP_SIN, OP_COS, Scope, sin, cos, ln, integral, indef, absolute
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


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
    int x ^ n dx  ->  x ^ (n + 1) / (n + 1)
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
    int x ^ n dx  ->  x ^ (n + 1) / (n + 1)
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


def match_constant_integral(node):
    """
    int c dx  ->  cx
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if not fx.contains(x):
        return [P(node, constant_integral)]

    return []


def constant_integral(root, args):
    """
    int c dx  ->  cx
    """
    c, x = root[:2]

    return solve_integral(root, c * x)


MESSAGES[constant_integral] = _('{0[0]} does not contain {0[1]}, so its ' \
        'integral over {0[1]} is its multiplication with {0[1]}.')


def match_factor_out_constant(node):
    """
    int cf(x) dx  ->  c int f(x) dx
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if not fx.is_op(OP_MUL):
        return []

    p = []
    scope = Scope(fx)

    for n in scope:
        if not n.contains(x):
            p.append(P(node, factor_out_constant, (scope, n)))

    return p


def factor_out_constant(root, args):
    """
    int cf(x) dx  ->  c int f(x) dx
    """
    scope, c = args
    scope.remove(c)

    return c * integral(scope.as_nary_node(), *root[1:])


MESSAGES[factor_out_constant] = _('Factor out {2} from integral {0}.')


def match_division_integral(node):
    """
    int 1 / x dx  ->  ln|x|
    int a / x dx  ->  int a(1 / x) dx  # -> a int 1 / x dx  ->  aln|x|
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if fx.is_op(OP_DIV) and fx[1] == x:
        if fx[0] == 1:
            return [P(node, division_integral)]

        return [P(node, extend_division_integral)]

    return []


def division_integral(root, args):
    """
    int 1 / x dx  ->  ln|x|
    """
    return solve_integral(root, ln(absolute(root[0][1])))


MESSAGES[division_integral] = \
        _('1 / {0[1]} has the standard anti-derivative ln|{0[1]}| + c.')


def extend_division_integral(root, args):
    """
    int a / x dx  ->  int a(1 / x) dx  # -> a int 1 / x dx  ->  aln|x|
    """
    a, x = root[0]

    return integral(a * (L(1) / x), *root[1:])


MESSAGES[extend_division_integral] = _('Bring nominator {0[0][0]} out of the' \
        ' fraction to obtain a standard 1 / {0[0][1]} integral.')


def match_function_integral(node):
    """
    int log_g(x) dx  ->  (xln(x) - x) / log_g(x)
    int sin(x) dx    ->  -cos(x)
    int cos(x) dx    ->  sin(x)
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if fx.is_leaf or fx[0] != x:
        return []

    if fx.op == OP_LOG:
        return [P(node, logarithm_integral)]

    if fx.op == OP_SIN:
        return [P(node, sinus_integral)]

    if fx.op == OP_COS:
        return [P(node, cosinus_integral)]

    return []


def logarithm_integral(root, args):
    """
    int log_g(x) dx  ->  (xln(x) - x) / log_g(x)
    """
    x, g = root[0]

    return solve_integral(root, (x * ln(x) - x) / ln(g))


MESSAGES[logarithm_integral] = _('log_g(x) has the standard anti-derivative ' \
        '(xln(x) - x) / log_g(x) + c.')


def sinus_integral(root, args):
    """
    int sin(x) dx  ->  -cos(x)
    """
    return solve_integral(root, -cos(root[0][0]))


MESSAGES[sinus_integral] = \
        _('{0[0]} has the standard anti-derivative -cos({0[0][0]}) + c.')


def cosinus_integral(root, args):
    """
    int cos(x) dx  ->  sin(x)
    """
    return solve_integral(root, sin(root[0][0]))


MESSAGES[cosinus_integral] = \
        _('{0[0]} has the standard anti-derivative sin({0[0][0]}) + c.')
