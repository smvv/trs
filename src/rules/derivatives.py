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
from .utils import find_variables, first_sorted_variable
from ..node import ExpressionLeaf as L, Scope, OP_DER, OP_MUL, OP_LOG, \
        OP_SIN, OP_COS, OP_TAN, OP_ADD, OP_DIV, E, sin, cos, der, ln
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def second_arg(node):
    """
    Get the second child of a node if it exists, None otherwise.
    """
    return node[1] if len(node) > 1 else None


def same_der(root, new):
    """
    Replace root with a new derrivative, using the same operator as root
    (OP_PRIME or DXDER).
    """
    return der(new, second_arg(root))


def get_derivation_variable(node, variables=None):
    """
    Find the variable to derive over.

    >>> print get_derivation_variable(der(L('x')))
    'x'
    """
    if len(node) > 1:
        assert node[1].is_identifier()
        return node[1].value

    if not variables:
        variables = find_variables(node)

    if not len(variables):
        return None

    return first_sorted_variable(variables)


def chain_rule(root, args):
    """
    Apply the chain rule:
    [f(g(x)]'  ->  f'(g(x)) * g'(x)

    f'(g(x)) is not expressable in the current syntax, so calculate it directly
    using the application function in the arguments. g'(x) is simply expressed
    as der(g(x), x).
    """
    g, f_deriv, f_deriv_args = args

    return f_deriv(root, f_deriv_args) * same_der(root, g)


MESSAGES[chain_rule] = _('Apply the chain rule to {0}.')


def match_zero_derivative(node):
    """
    der(x, y)  ->  0
    der(n)     ->  0
    """
    assert node.is_op(OP_DER)

    variables = find_variables(node[0])
    var = get_derivation_variable(node, variables)

    if not var or var not in variables:
        return [P(node, zero_derivative)]

    return []


def zero_derivative(root, args):
    """
    der(x, y)  ->  0
    der(n)     ->  0
    """
    return L(0)


MESSAGES[zero_derivative] = _('Constant {0[0]} has derivative 0.')


def match_one_derivative(node):
    """
    der(x)     ->  1  # Implicit x
    der(x, x)  ->  1  # Explicit x
    """
    assert node.is_op(OP_DER)

    var = get_derivation_variable(node)

    if var and node[0] == L(var):
        return [P(node, one_derivative)]

    return []


def one_derivative(root, args):
    """
    der(x)     ->  1
    der(x, x)  ->  1
    """
    return L(1)


MESSAGES[one_derivative] = _('Variable {0[0]} has derivative 1.')


def match_const_deriv_multiplication(node):
    """
    der(c * f(x), x)  ->  c * der(f(x), x)
    """
    assert node.is_op(OP_DER)

    p = []

    if node[0].is_op(OP_MUL):
        x = L(get_derivation_variable(node))
        scope = Scope(node[0])

        for n in scope:
            if not n.contains(x):
                p.append(P(node, const_deriv_multiplication, (scope, n, x)))

    return p


def const_deriv_multiplication(root, args):
    """
    der(c * f(x), x)  ->  c * der(f(x), x)
    """
    scope, c, x = args

    scope.remove(c)

    return c * same_der(root, scope.as_nary_node())


MESSAGES[const_deriv_multiplication] = \
        _('Bring multiplication with {2} in derivative {0} to the outside.')


def match_variable_power(node):
    """
    der(x ^ n)           ->  n * x ^ (n - 1)
    der(x ^ n, x)        ->  n * x ^ (n - 1)
    der(f(x) ^ n)        ->  n * f(x) ^ (n - 1) * der(f(x))  # Chain rule
    der(f(x) ^ g(x), x)  ->  der(e ^ ln(f(x) ^ g(x)), x)
    """
    assert node.is_op(OP_DER)

    if not node[0].is_power():
        return []

    root, exponent = node[0]

    rvars = find_variables(root)
    evars = find_variables(exponent)
    x = get_derivation_variable(node, rvars | evars)

    if x in rvars:
        if x in evars:
            return [P(node, power_rule)]

        if root.is_variable():
            return [P(node, variable_root)]

        return [P(node, chain_rule, (root, variable_root, ()))]

    if exponent.is_variable():
        return [P(node, variable_exponent)]

    return [P(node, chain_rule, (exponent, variable_exponent, ()))]


def power_rule(root, args):
    """
    [f(x) ^ g(x)]'  ->  [e ^ ln(f(x) ^ g(x))]'
    """
    return same_der(root, L(E) ** ln(root[0]))


MESSAGES[power_rule] = \
        _('Write {0} as a logarithm to be able to separate root and exponent.')


def variable_root(root, args):
    """
    der(x ^ n, x)  ->  n * x ^ (n - 1)
    """
    x, n = root[0]

    return (n).negate(root[0].negated) * x ** (n - 1)


MESSAGES[variable_root] = \
        _('Apply standard derivative `d/dx x ^ n = n * x ^ (n - 1)` to {0}.')


def variable_exponent(root, args):
    """
    der(g ^ x, x)  ->  g ^ x * ln(g)

    Shortcut rule (because of presence of formula list):
    der(e ^ x, x)  ->  e ^ x
    """
    g, x = root[0]

    if g == E:
        return (g ** x).negate(root[0].negated)

    return (g ** x).negate(root[0].negated) * ln(g)


MESSAGES[variable_exponent] = \
        _('Apply standard derivative `d/dx g ^ x = g ^ x * ln g` to {0}.')


def match_logarithmic(node):
    """
    der(log(x, g), x)     ->  1 / (x * ln(g))
    der(log(f(x), g), x)  ->  1 / (f(x) * ln(g)) * der(f(x), x)
    """
    assert node.is_op(OP_DER)

    x = get_derivation_variable(node)

    if x and node[0].is_op(OP_LOG):
        f = node[0][0]
        x = L(x)

        if f == x:
            return [P(node, logarithmic, ())]

        if f.contains(x):
            return [P(node, chain_rule, (f, logarithmic, ()))]

    return []


def logarithmic(root, args):
    """
    der(log(x, g), x)  ->  1 / (xln(g))

    Shortcut function (because of presence on formula list):
    der(ln(x), x)      ->  1 / x
    """
    x, g = root[0]

    if g == E:
        return L(1) / x

    return L(1) / (x * ln(g))


MESSAGES[logarithmic] = \
        _('Apply standard derivative `d/dx log(x, g) = 1 / (x * ln(g))`.')


def match_goniometric(node):
    """
    der(sin(x), x)     ->  cos(x)
    der(sin(f(x)), x)  ->  cos(f(x)) * der(f(x), x)
    der(cos(x), x)     ->  -sin(x)
    der(cos(f(x)), x)  ->  -sin(f(x)) * der(f(x), x)
    der(tan(x), x)     ->  der(sin(x) / cos(x), x)
    """
    assert node.is_op(OP_DER)

    x = get_derivation_variable(node)

    if x and not node[0].is_leaf:
        op = node[0].op

        if op in (OP_SIN, OP_COS):
            f = node[0][0]
            x = L(x)
            handler = sinus if op == OP_SIN else cosinus

            if f == x:
                return [P(node, handler)]

            if f.contains(x):
                return [P(node, chain_rule, (f, handler, ()))]

        if op == OP_TAN:
            return [P(node, tangens)]

    return []


def sinus(root, args):
    """
    der(sin(x), x)  ->  cos(x)
    """
    return cos(root[0][0])


MESSAGES[sinus] = _('Apply standard derivative `d/dx sin(x)` = `cos(x)`.')


def cosinus(root, args):
    """
    der(cos(x), x)  ->  -sin(x)
    """
    return -sin(root[0][0])


MESSAGES[cosinus] = _('Apply standard derivative `d/dx cos(x)` = `-sin(x)`.')


def tangens(root, args):
    """
    der(tan(x), x)  ->  der(sin(x) / cos(x), x)
    """
    x = root[0][0]

    return same_der(root, sin(x) / cos(x))


MESSAGES[tangens] = \
        _('Convert the tangens to a division and apply the product rule.')


def match_sum_product_rule(node):
    """
    [f(x) + g(x)]'  ->  f'(x) + g'(x)
    [f(x) * g(x)]'  ->  f'(x) * g(x) + f(x) * g'(x)
    """
    assert node.is_op(OP_DER)

    x = get_derivation_variable(node)

    if not x or node[0].is_leaf or node[0].op not in (OP_ADD, OP_MUL):
        return []

    scope = Scope(node[0])
    x = L(x)
    functions = [n for n in scope if n.contains(x)]

    if node[0].op == OP_MUL:
        if len(functions) < 2:
            return []

        handler = product_rule
    else:
        handler = sum_rule

    return [P(node, handler, (scope, f)) for f in functions]


def sum_rule(root, args):
    """
    [f(x) + g(x)]'  ->  f'(x) + g'(x)
    """
    scope, f = args
    scope.remove(f)

    return same_der(root, f) + same_der(root, scope.as_nary_node())


MESSAGES[sum_rule] = _('Apply the sum rule to {0}.')


def product_rule(root, args):
    """
    [f(x) * g(x)]'  ->  f'(x) * g(x) + f(x) * g'(x)

    Note that implicitely:
    [f(x) * g(x) * h(x)]'  ->  f'(x) * (g(x) * h(x)) + f(x) * [g(x) * h(x)]'
    """
    scope, f = args
    scope.remove(f)
    gh = scope.as_nary_node()

    return same_der(root, f) * gh + f * same_der(root, gh)


MESSAGES[product_rule] = _('Apply the product rule to {0}.')


def match_quotient_rule(node):
    """
    [f(x) / g(x)]'  ->  (f'(x) * g(x) - f(x) * g'(x)) / g(x) ^ 2
    """
    assert node.is_op(OP_DER)

    x = get_derivation_variable(node)

    if not x or not node[0].is_op(OP_DIV):
        return []

    f, g = node[0]
    x = L(x)

    if f.contains(x) and g.contains(x):
        return [P(node, quotient_rule)]

    return []


def quotient_rule(root, args):
    """
    [f(x) / g(x)]'  ->  (f'(x) * g(x) - f(x) * g'(x)) / g(x) ^ 2
    """
    f, g = root[0]

    return (same_der(root, f) * g - f * same_der(root, g)) / g ** 2


MESSAGES[quotient_rule] = _('Apply the quotient rule to {0}.')
