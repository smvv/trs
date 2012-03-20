from itertools import combinations

from ..node import ExpressionNode as N, ExpressionLeaf as L, OP_LOG, E, \
        OP_ADD, OP_MUL, Scope
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def log(exponent, base=10):
    if not isinstance(base, L):
        base = L(base)

    return N(OP_LOG, exponent, base)


def ln(exponent):
    return log(exponent, base=E)


def match_constant_logarithm(node):
    """
    log_1(a)   ->  # raise ValueError for base 1
    log(1)     ->  0
    log(a, a)  ->  log(a) / log(a)  # ->  1
    """
    # TODO: base and raised
    assert node.is_op(OP_LOG)

    raised, base = node

    if base == 1:
        raise ValueError('Logarithm with base 1 does not exist.')

    p = []

    if raised == 1:
        p.append(P(node, logarithm_of_one))

    if raised == base:
        p.append(P(node, divide_same_base))

    return p


def logarithm_of_one(root, args):
    """
    log(1)  ->  0
    """
    raised, base = root

    return log(raised) / log(base)


MESSAGES[logarithm_of_one] = _('Logarithm of one reduces to zero.')


def divide_same_base(root, args):
    """
    log(a, b)  ->  log(a) / log(b)
    """
    raised, base = root

    return log(raised) / log(base)


MESSAGES[divide_same_base] = _('Apply log_b(a)  ->  log(a) / log(b).')


def match_add_logarithms(node):
    """
    log(a) + log(b)   ->  log(ab)
    -log(a) - log(b)  ->  -(log(a) + log(b))  # ->  -log(ab)
    log(a) - log(b)   ->  log(a / b)
    -log(a) + log(b)  ->  log(b / a)
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)
    logarithms = filter(lambda n: n.is_op(OP_LOG), scope)

    for log_a, log_b in combinations(logarithms, 2):
        # Compare base
        if log_a[1] != log_b[1]:
            continue

        a_negated = log_a.negated == 1
        b_negated = log_b.negated == 1

        if not log_a.negated and not log_b.negated:
            # log(a) + log(b)  ->  log(ab)
            p.append(P(node, add_logarithms, (scope, log_a, log_b)))
        elif a_negated and b_negated:
            # -log(a) - log(b)  ->  -(log(a) + log(b))
            p.append(P(node, expand_negations, (scope, log_a, log_b)))
        elif not log_a.negated and b_negated:
            # log(a) - log(b)  ->  log(a / b)
            p.append(P(node, subtract_logarithms, (scope, log_a, log_b)))
        elif a_negated and not log_b.negated:
            # -log(a) + log(b)  ->  log(b / a)
            p.append(P(node, subtract_logarithms, (scope, log_b, log_a)))

    return p


def add_logarithms(root, args):
    """
    log(a) + log(b)  ->  log(ab)
    """
    scope, log_a, log_b = args
    a, base = log_a
    b = log_b[0]

    scope.replace(log_a, log(a * b, base=base))
    scope.remove(log_b)

    return scope.as_nary_node()


MESSAGES[add_logarithms] = _('Apply log(a) + log(b) = log(ab).')
        #_('Combine two logarithms with the same base: {2} and {3}.')


def expand_negations(root, args):
    """
    -log(a) - log(b)  ->  -(log(a) + log(b))  # ->  -log(ab)
    """
    scope, log_a, log_b = args

    scope.replace(log_a, -(+log_a + +log_b))
    scope.remove(log_b)

    return scope.as_nary_node()


MESSAGES[expand_negations] = \
        _('Apply -log(a) - log(b) = -(log(a) + log(b)).')


def subtract_logarithms(root, args):
    """
    log(a) - log(b)  ->  log(a / b)
    """
    scope, log_a, log_b = args
    a, base = log_a
    b = log_b[0]

    scope.replace(log_a, log(a / b, base=base))
    scope.remove(log_b)

    return scope.as_nary_node()


MESSAGES[subtract_logarithms] = _('Apply log(a) - log(b) = log(a / b).')
