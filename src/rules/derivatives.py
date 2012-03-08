from itertools import combinations

from .utils import find_variables
from ..node import Scope, OP_DERIV, ExpressionNode as N, ExpressionLeaf as L
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


def match_constant_derivative(node):
    """
    der(x)     ->  1
    der(x, x)  ->  1
    der(x, y)  ->  x
    der(n)     ->  0
    """
    assert node.is_op(OP_DERIV)

    variables = find_variables(node[0])
    var = get_derivation_variable(node, variables=variables)

    if not var or var not in variables:
        return [P(node, zero_derivative, ())]

    if (node[0] == node[1] if len(node) > 1 else node[0].is_variable()):
        return [P(node, one_derivative, ())]

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
    der(n)  ->  0
    """
    return L(0)


MESSAGES[zero_derivative] = _('Constant {0[0]} has derivative 0.')


def match_variable_power(node):
    """
    der(x ^ n)     ->  n * x ^ (n - 1)
    der(x ^ n, x)  ->  n * x ^ (n - 1)
    der(x ^ f(x))  ->  n * x ^ (n - 1)
    """
    assert node.is_op(OP_DERIV)

    if node[0].is_power():
        x, n = node[0]

        if x.is_variable():
            return [P(node, variable_power, ())]

    return []


def variable_power(root, args):
    """
    der(x ^ n, x)  ->  n * x ^ (n - 1)
    """
    x, n = args

    return n * x ^ (n - 1)
