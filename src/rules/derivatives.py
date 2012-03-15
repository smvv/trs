from itertools import combinations

from .utils import find_variables
from .logarithmic import ln
from .goniometry import sin, cos
from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, OP_DER, \
        OP_MUL, OP_LOG, OP_SIN, OP_COS, OP_TAN
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def der(f, x=None):
    return N('der', f, x) if x else N('der', f)


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

    if len(variables) > 1:
        # FIXME: Use first variable, sorted alphabetically?
        #return sorted(variables)[0]
        raise ValueError('More than 1 variable in implicit derivative: '
                         + ', '.join(variables))

    if not len(variables):
        return None

    return list(variables)[0]


def chain_rule(root, args):
    """
    Apply the chain rule:
    [f(g(x)]'  ->  f'(g(x)) * g'(x)

    f'(g(x)) is not expressable in the current syntax, so calculate it directly
    using the application function in the arguments. g'(x) is simply expressed
    as der(g(x), x).
    """
    g, f_deriv, f_deriv_args = args
    x = root[1] if len(root) > 1 else None

    return f_deriv(root, f_deriv_args) * der(g, x)


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


def zero_derivative(root, args):
    """
    der(x, y)  ->  0
    der(n)     ->  0
    """
    return L(0)


MESSAGES[zero_derivative] = _('Constant {0[0]} has derivative 0.')


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

    return c * der(scope.as_nary_node(), x)


MESSAGES[const_deriv_multiplication] = \
        _('Bring multiplication with {2} in derivative {0} to the outside.')


def match_variable_power(node):
    """
    der(x ^ n)     ->  n * x ^ (n - 1)
    der(x ^ n, x)  ->  n * x ^ (n - 1)
    der(f(x) ^ n)  ->  n * f(x) ^ (n - 1) * der(f(x))  # Chain rule
    """
    assert node.is_op(OP_DER)

    if not node[0].is_power():
        return []

    root, exponent = node[0]

    rvars = find_variables(root)
    evars = find_variables(exponent)
    x = get_derivation_variable(node, rvars | evars)

    if x in rvars and x not in evars:
        if root.is_variable():
            return [P(node, variable_root)]

        return [P(node, chain_rule, (root, variable_root, ()))]
    elif not x in rvars and x in evars:
        if exponent.is_variable():
            return [P(node, variable_exponent)]

        return [P(node, chain_rule, (exponent, variable_exponent, ()))]

    return []


def variable_root(root, args):
    """
    der(x ^ n, x)  ->  n * x ^ (n - 1)
    """
    x, n = root[0]

    return n * x ** (n - 1)


MESSAGES[variable_root] = \
        _('Apply standard derivative d/dx x ^ n = n * x ^ (n - 1) on {0}.')


def variable_exponent(root, args):
    """
    der(g ^ x, x)  ->  g ^ x * ln(g)

    Note that (in combination with logarithmic/constant rules):
    der(e ^ x)  ->  e ^ x * ln(e)  ->  e ^ x * 1  ->  e ^ x
    """
    # TODO: Put above example 'der(e ^ x)' in unit test
    g, x = root[0]

    return g ** x * ln(g)


MESSAGES[variable_exponent] = \
        _('Apply standard derivative d/dx g ^ x = g ^ x * ln g.')


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
    der(log(x, g), x)  ->  1 / (x * ln(g))
    """
    x, g = root[0]

    return L(1) / (x * ln(g))


MESSAGES[logarithmic] = \
        _('Apply standard derivative d/dx log(x, g) = 1 / (x * ln(g)).')


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


MESSAGES[sinus] = _('Apply standard derivative d/dx sin(x) = cos(x).')


def cosinus(root, args):
    """
    der(cos(x), x)  ->  -sin(x)
    """
    return -sin(root[0][0])


MESSAGES[cosinus] = _('Apply standard derivative d/dx cos(x) = -sin(x).')


def tangens(root, args):
    """
    der(tan(x), x)  ->  der(sin(x) / cos(x), x)
    """
    f = root[0][0]
    x = root[1] if len(root) > 1 else None

    return der(sin(f) / cos(f), x)


MESSAGES[tangens] = \
        _('Convert the tanges to a division and apply the product rule.')
