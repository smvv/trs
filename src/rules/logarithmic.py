from itertools import combinations, product, ifilterfalse
import math

from .utils import find_variables, partition, divides, is_numeric_node
from ..node import ExpressionLeaf as L, OP_LOG, OP_ADD, OP_MUL, OP_POW, \
        Scope, log, DEFAULT_LOGARITHM_BASE, E, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_constant_logarithm(node):
    """
    log_1(a)   ->  # raise ValueError for base 1
    log(1)     ->  0
    log(a, a)  ->  1
    log(a, b) and b not in  (10, e)  ->  log(a) / log(b)
    """
    assert node.is_op(OP_LOG)

    raised, base = node

    if base == 1:
        raise ValueError('Logarithm with base 1 does not exist.')

    p = []

    if raised == 1:
        # log(1)  ->  0
        p.append(P(node, logarithm_of_one))

    if raised == base:
        # log(a, a)  ->  1
        p.append(P(node, base_equals_raised))
        p.append(P(node, divide_same_base))
    elif base not in (DEFAULT_LOGARITHM_BASE, E):
        # log(a, b)  ->  log(a) / log(b)
        p.append(P(node, divide_same_base))

    return p


def logarithm_of_one(root, args):
    """
    log(1)  ->  0
    """
    raised, base = root

    return L(0).negate(root.negated)


MESSAGES[logarithm_of_one] = _('Logarithm of one reduces to zero.')


def base_equals_raised(root, args):
    """
    log(a, a)  ->  1
    """
    return L(1).negate(root.negated)


MESSAGES[base_equals_raised] = _('Logarithm {0} reduces to 1.')


def divide_same_base(root, args):
    """
    log(a, b) and b != 10  ->  log(a) / log(b)
    """
    raised, base = root

    return log(raised) / log(base)


MESSAGES[divide_same_base] = _('Apply log_b(a) = log(a) / log(b) on {0}.')


def match_add_logarithms(node):
    """
    log(a) + log(b) and a,b in Z   ->  log(ab)
    -log(a) - log(b) and a,b in Z  ->  -(log(a) + log(b))  # ->  -log(ab)
    log(a) - log(b) and a/b in Z   ->  log(a / b)
    -log(a) + log(b) and a/b in Z  ->  log(b / a)
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)
    logarithms = filter(lambda n: n.is_op(OP_LOG), scope)

    for log_a, log_b in combinations(logarithms, 2):
        # Compare base
        (a, base_a), (b, base_b) = log_a, log_b

        if base_a != base_b or not a.is_numeric() \
                or not b.is_numeric():  # pragma: nocover
            continue

        a_negated = log_a.negated == 1
        b_negated = log_b.negated == 1

        if not log_a.negated and not log_b.negated:
            # log(a) + log(b)  ->  log(ab)
            p.append(P(node, add_logarithms, (scope, log_a, log_b)))
        elif a_negated and b_negated:
            # -log(a) - log(b)  ->  -(log(a) + log(b))
            p.append(P(node, expand_negations, (scope, log_a, log_b)))
        elif not log_a.negated and b_negated and divides(b.value, a.value):
            # log(a) - log(b)  ->  log(a / b)
            p.append(P(node, subtract_logarithms, (scope, log_a, log_b)))
        elif a_negated and not log_b.negated and  divides(a.value, b.value):
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
        #_('Combine logarithms with the same base: {2} and {3}.')


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


def match_raised_base(node):
    """
    g ^ log_g(a)        ->  a
    g ^ (b * log_g(a))  ->  g ^ log_g(a ^ b)
    """
    assert node.is_op(OP_POW)

    root, exponent = node

    if exponent.is_op(OP_LOG) and exponent[1] == root:
        return [P(node, raised_base, (exponent[0],))]

    p = []

    if exponent.is_op(OP_MUL):
        scope = Scope(exponent)
        is_matching_logarithm = lambda n: n.is_op(OP_LOG) and n[1] == root
        logs, others = partition(is_matching_logarithm, scope)

        for other, log in product(others, logs):
            # Add this possibility so that a 'raised_base' possibility is
            # generated in the following iteration
            p.append(P(node, factor_in_exponent_multiplicant,
                       (scope, other, log)))

    return p


def factor_in_exponent_multiplicant(root, args):
    """
    g ^ (b * log_g(a))  ->  g ^ log_g(a ^ b)
    """
    r, e = root

    return r ** factor_in_multiplicant(e, args)


MESSAGES[factor_in_exponent_multiplicant] = \
        _('Bring {2} into {3} as exponent so that the power can be removed.')


def raised_base(root, args):
    """
    g ^ log_g(a)  ->  a
    """
    return args[0]


MESSAGES[raised_base] = _('Apply g ^ log_g(a) = a on {0}.')


def match_factor_out_exponent(node):
    """
    This match simplifies a power with a variable in it to a multiplication:
    log(a ^ b)   ->  blog(a)
    log(a ^ -b)  ->  log((a ^ b) ^ -1)  # =>*  -log(a ^ b)
    log(b, a) and a ** y = b with y in Z  ->  log(a ^ y, a)  # =>* y
    """
    assert node.is_op(OP_LOG)

    p = []
    exp, base = node

    if exp.is_power():
        a, b = exp

        if b.negated:
            p.append(P(node, split_negative_exponent))

        if a == base:
            p.append(P(node, factor_out_exponent_important))
        else:
            p.append(P(node, factor_out_exponent))
    elif exp.is_numeric() and not exp.negated:
        b, a = exp.value, base.value
        y = int(round(math.log(b, a)))

        if b == a ** y:
            p.append(P(node, make_raised_base, (y,)))

    return p


def split_negative_exponent(root, args):
    """
    log(a ^ -b)  ->  log((a ^ b) ^ -1)  # =>*  -log(a ^ b)
    """
    (a, b), base = root

    return log((a ** +b) ** -L(1), base=base)


MESSAGES[split_negative_exponent] = \
        _('Split and factor out the negative exponent within logarithm {0}.')


def factor_out_exponent(root, args):
    """
    log(a ^ b)  ->  blog(a)
    """
    (a, b), base = root

    return b * log(a, base=base)


MESSAGES[factor_out_exponent] = _('Factor out exponent {0[0][1]} from {0}.')


def factor_out_exponent_important(root, args):
    return factor_out_exponent(root, args)


MESSAGES[factor_out_exponent_important] = MESSAGES[factor_out_exponent]


def make_raised_base(root, args):
    """
    log(b, a) and b ** y = a with y in Z  ->  log(a ^ y, a)  # =>* y
    """
    exp, base = root
    y = L(args[0])

    return log(base.clone() ** y, base=base).negate(root.negated)


MESSAGES[make_raised_base] = _('Write {0[0]} as a power of {0[1]}.')


def match_factor_in_multiplicant(node):
    """
    Only bring a multiplicant inside a logarithm if both the multiplicant and
    the logaritm's content are constants. This will yield a new simplification
    of constants inside the logarithm.
    2log(2)      ->  log(2 ^ 2)        # -> log(4)
    2log(2 / 4)  ->  log((2 / 4) ^ 2)  # =>* log(1 / 4)
    """
    assert node.is_op(OP_MUL)

    scope = Scope(node)
    constants = filter(lambda n: n.is_int(), scope)
    logarithms = filter(lambda n: n.is_op(OP_LOG) \
                                  and not len(find_variables(n)), scope)
    p = []

    for constant, logarithm in product(constants, logarithms):
        p.append(P(node, factor_in_multiplicant, (scope, constant, logarithm)))

    return p


def factor_in_multiplicant(root, args):
    """
    alog(b)  ->  log(b ^ a)
    """
    scope, a, log_b = args
    b, base = log_b
    scope.replace(a, log(b ** a, base=base))
    scope.remove(log_b)

    return scope.as_nary_node()


MESSAGES[factor_in_multiplicant] = \
        _('Bring multiplicant {2} into {3} as the exponent of {3[0]}.')


def match_expand_terms(node):
    """
    log(ab) and a not in Z  ->  log(a) + log(b)
    log(a / b)              ->  log(a) - log(b)
    """
    assert node.is_op(OP_LOG)

    exp = node[0]

    if exp.is_op(OP_MUL):
        scope = Scope(exp)

        return [P(node, expand_multiplication_terms, (scope, n)) \
                for n in ifilterfalse(is_numeric_node, scope)]

    if exp.is_op(OP_DIV):
        return [P(node, expand_division_terms)]

    return []


def expand_multiplication_terms(root, args):
    """
    log(ab) and a not in Z  ->  log(a) + log(b)
    """
    scope, n = args
    scope.remove(n)
    base = root[1]
    addition = log(n, base=base) + log(scope.as_nary_node(), base=base)

    return addition.negate(root.negated)


MESSAGES[expand_multiplication_terms] = _('Extract {2} from {0}.')


def expand_division_terms(root, args):
    """
    log(a / b)  ->  log(a) - log(b)
    """
    division, base = root
    n, d = division
    addition = log(n.negate(division.negated), base=base) - log(d, base=base)

    return addition.negate(root.negated)


MESSAGES[expand_division_terms] = _('Expand {0} to a subtraction.')
