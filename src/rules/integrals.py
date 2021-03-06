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
from .utils import find_variables, substitute, find_variable
from ..node import ExpressionLeaf as L, OP_INT, OP_INT_DEF, OP_MUL, OP_DIV, \
        OP_LOG, OP_SIN, OP_COS, Scope, sin, cos, ln, integral, int_def, \
        absolute, OP_ADD, negate
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def choose_constant(integral):
    """
    Choose a constant to be added to the antiderivative.
    Start at 'c', then alphabetically from 'a' until an variable is encountered
    that is not occupied in the integral already.
    """
    occupied = find_variables(integral)
    c = 'c'
    i = 96

    while c in occupied:
        # Skip 'c'
        i += 2 if i == 98 else 1
        c = chr(i)

    return L(c.upper())


def solve_integral(integral, F):
    """
    Solve an integral given its anti-derivative F:
    - First, finish the anti-derivative by adding a constant.
    - If no bounds are specified, return the anti-derivative.
    - Given a lower bound a and upper bound b, the solution is the definite
      integral [F(x)]_a^b. If F(x) contains multiple variables so that the 'x'
      is not identified by 'find_variable(F)' (which is used by the definite
      integral), skip the reduction of the definite integral and return the
      solution F(b) - F(a).
    """
    F += choose_constant(integral)

    if len(integral) < 3:
        solution = F
    else:
        x, lbnd, ubnd = integral[1:4]

        if x != find_variable(F):
            solution = substitute(F, x, ubnd) - substitute(F, x, lbnd)
        else:
            solution = int_def(F, lbnd, ubnd)

    return negate(solution, integral.negated)


def match_solve_definite(node):
    """
    [F(x)]_a^b  ->  F(b) - F(a)
    """
    assert node.is_op(OP_INT_DEF)

    return [P(node, solve_definite)]


def solve_definite(root, args):
    """
    [F(x)]_a^b  ->  F(b) - F(a)
    """
    Fx, a, b = root
    x = find_variable(Fx)

    return negate(substitute(Fx, x, b) - substitute(Fx, x, a), root.negated)


def solve_definite_msg(root, args):  # pragma: nocover
    return _('Solve definite integral {0} using substitution ' \
             'of `%s` with {0[2]} and {0[1]}.' % find_variable(root[0]))


MESSAGES[solve_definite] = solve_definite_msg


def match_integrate_variable_power(node):
    """
    int x ^ n dx  ->  1 / (n + 1) * x ^ (n + 1)
    int g ^ x dx  ->  g ^ x / ln(g)
    """
    assert node.is_op(OP_INT)

    f, x = node[:2]

    if f.is_power() and not f.negated:
        root, exponent = f

        if root == x and not exponent.contains(x):
            return [P(node, integrate_variable_root)]

        if exponent == x and not root.contains(x):
            return [P(node, integrate_variable_exponent)]

    return []


def integrate_variable_root(root, args):
    """
    int x ^ n dx  ->  1 / (n + 1) * x ^ (n + 1)
    """
    x, n = root[0]

    return solve_integral(root, L(1) / (n + 1) * x ** (n + 1))


MESSAGES[integrate_variable_root] = _('Apply standard integral ' \
        '`int(x ^ n) = 1 / (n + 1) * x ^ (n + 1) + c`.')


def integrate_variable_exponent(root, args):
    """
    int g ^ x dx  ->  g ^ x / ln(g)
    """
    g, x = root[0]

    return solve_integral(root, g ** x / ln(g))


MESSAGES[integrate_variable_exponent] = \
        _('Apply standard integral `int(g ^ x) = g ^ x / ln(g) + c`.')


def match_constant_integral(node):
    """
    int x dx  ->  int x ^ 1 dx  # ->  x ^ 2 / 2 + c
    int c dx  ->  cx
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if fx == x:
        return [P(node, single_variable_integral)]

    if not fx.contains(x):
        return [P(node, constant_integral)]

    return []


def single_variable_integral(root, args):
    """
    int x dx  ->  int x ^ 1 dx  # ->  x ^ 2 / 2 + c
    """
    return integral(root[0] ** 1, *root[1:])


MESSAGES[single_variable_integral] = _('Rewrite {0[0]} to `{0[0]} ^ 1` and ' \
        'apply the standard integral for `{0[0]} ^ n`.')


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
    int -f(x) dx  ->  -1 int f(x) dx
    """
    assert node.is_op(OP_INT)

    fx, x = node[:2]

    if fx.negated:
        return [P(node, factor_out_integral_negation)]

    if not fx.is_op(OP_MUL):
        return []

    p = []
    scope = Scope(fx)

    for n in scope:
        if not n.contains(x):
            p.append(P(node, factor_out_constant, (scope, n)))

    return p


def factor_out_integral_negation(root, args):
    """
    int -f(x) dx  ->  int -1 * f(x) dx  # =>*  -int f(x) dx
    """
    return -integral(root[0].reduce_negation(), *root[1:])


MESSAGES[factor_out_integral_negation] = \
        _('Bring the negation of {0[0]} outside of the integral.')


def factor_out_constant(root, args):
    """
    int cf(x) dx  ->  c int f(x) dx
    """
    scope, c = args
    scope.remove(c)

    return negate(c * integral(scope.as_nary_node(), *root[1:]), root.negated)


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
        _('`1 / {0[1]}` has the standard anti-derivative `ln|{0[1]}| + c`.')


def extend_division_integral(root, args):
    """
    int a / x dx  ->  int a(1 / x) dx  # -> a int 1 / x dx  ->  aln|x|
    """
    a, x = root[0]

    return integral(a * (L(1) / x), *root[1:])


MESSAGES[extend_division_integral] = _('Bring nominator {0[0][0]} out of the' \
        ' fraction to obtain a standard `1 / {0[0][1]}` integral.')


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


MESSAGES[logarithm_integral] = _('`log_g(x)` has the standard ' \
        'anti-derivative `(xln(x) - x) / log_g(x) + c`.')


def sinus_integral(root, args):
    """
    int sin(x) dx  ->  -cos(x)
    """
    return solve_integral(root, -cos(root[0][0]))


MESSAGES[sinus_integral] = \
        _('{0[0]} has the standard anti-derivative `-cos({0[0][0]}) + c`.')


def cosinus_integral(root, args):
    """
    int cos(x) dx  ->  sin(x)
    """
    return solve_integral(root, sin(root[0][0]))


MESSAGES[cosinus_integral] = \
        _('{0[0]} has the standard anti-derivative `sin({0[0][0]}) + c`.')


def match_sum_rule_integral(node):
    """
    int f(x) + g(x) dx  ->  int f(x) dx + int g(x) dx
    """
    assert node.is_op(OP_INT)

    if not node[0].is_op(OP_ADD):
        return []

    scope = Scope(node[0])

    if len(scope) == 2:
        return [P(node, sum_rule_integral, (scope, scope[0]))]

    return [P(node, sum_rule_integral, (scope, n)) for n in scope]


def sum_rule_integral(root, args):
    """
    int f(x) + g(x) dx  ->  int f(x) dx + int g(x) dx
    """
    scope, f = args
    args = root[1:]
    scope.remove(f)
    addition = integral(f, *args) + integral(scope.as_nary_node(), *args)

    return negate(addition, root.negated)


MESSAGES[sum_rule_integral] = _('Apply the sum rule to {0}.')


def match_remove_definite_constant(node):
    """
    [f(x) + c]_a^b  ->  [f(x)]_a^b
    """
    assert node.is_op(OP_INT_DEF)

    if not node[0].is_op(OP_ADD):
        return []

    scope = Scope(node[0])
    x = find_variable(node[0])
    constants = [n for n in scope if not n.contains(x)]

    return [P(node, remove_definite_constant, (scope, c)) for c in constants]


def remove_definite_constant(root, args):
    """
    [f(x) + c]_a^b  ->  [f(x)]_a^b
    """
    scope, c = args
    scope.remove(c)
    Fx = scope.as_nary_node()
    a, b = root[1:]

    return negate(int_def(Fx, a, b), root.negated)


MESSAGES[remove_definite_constant] = \
        _('Remove constant {2} from definite integral.')
