from itertools import combinations, product

from .utils import least_common_multiple, partition, is_numeric_node, \
        evals_to_numeric
from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, OP_DIV, \
        OP_ADD, OP_MUL, OP_POW, nary_node, negate
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_constant_division(node):
    """
    a / 0  ->  Division by zero
    a / 1  ->  a
    0 / a  ->  0
    a / a  ->  1
    """
    assert node.is_op(OP_DIV)

    p = []
    nominator, denominator = node

    # a / 0
    if denominator == 0:
        raise ZeroDivisionError('Division by zero: %s.' % node)

    # a / 1
    if denominator == 1:
        p.append(P(node, division_by_one, (nominator,)))

    # 0 / a
    if nominator == 0:
        p.append(P(node, division_of_zero, (denominator,)))

    # a / a
    if nominator == denominator:
        p.append(P(node, division_by_self, (nominator,)))

    return p


def division_by_one(root, args):
    """
    a / 1  ->  a
    """
    return args[0]


MESSAGES[division_by_one] = _('Division by 1 yields the nominator.')


def division_of_zero(root, args):
    """
    0 / a  ->  0
    """
    return L(0)


MESSAGES[division_of_zero] = _('Division of 0 by {1} reduces to 0.')


def division_by_self(root, args):
    """
    a / a  ->  1
    """
    return L(1)


MESSAGES[division_by_self] = _('Division of {1} by itself reduces to 1.')


def match_add_fractions(node):
    """
    a / b + c / b and a, c in Z        ->  (a + c) / b
    a / b + c / d and a, b, c, d in Z  ->  a' / e + c' / e  # e = lcm(b, d)
                                                            # | e = b * d
    a / b + c and a, b, c in Z         ->  a / b + b / b * c # =>* (a + bc) / b
    """
    assert node.is_op(OP_ADD)

    p = []
    scope = Scope(node)
    fractions, others = partition(lambda n: n.is_op(OP_DIV), scope)
    numerics = filter(is_numeric_node, others)

    for ab, cd in combinations(fractions, 2):
        a, b = ab
        c, d = cd

        if b == d:
            # Equal denominators, add nominators to create a single fraction
            p.append(P(node, add_nominators, (scope, ab, cd)))
        elif all(map(is_numeric_node, (a, b, c, d))):
            # Denominators are both numeric, rewrite both fractions to the
            # least common multiple of their denominators. Later, the
            # nominators will be added
            lcm = least_common_multiple(b.value, d.value)
            p.append(P(node, equalize_denominators, (scope, ab, cd, lcm)))

            # Also, add the (non-recommended) possibility to multiply the
            # denominators. Do this only if the multiplication is not equal to
            # the least common multiple, to avoid duplicate possibilities
            mult = b.value * d.value

            if mult != lcm:
                p.append(P(node, equalize_denominators, (scope, ab, cd, mult)))

    for ab, c in product(fractions, numerics):
        a, b = ab

        if a.is_numeric() and b.is_numeric():
            # Fraction of constants added to a constant -> create a single
            # constant fraction
            p.append(P(node, constant_to_fraction, (scope, ab, c)))

    return p


def add_nominators(root, args):
    """
    a / b + c / b and a, c in Z  ->  (a + c) / b
    """
    scope, ab, cb = args
    a, b = ab
    c = cb[0]

    # Replace the left node with the new expression, transfer fraction
    # negations to nominators
    scope.replace(ab, (a.negate(ab.negated) + c.negate(cb.negated)) / b)
    scope.remove(cb)

    return scope.as_nary_node()


MESSAGES[add_nominators] = \
        _('Add the nominators of {2} and {3} to create a single fraction.')


def equalize_denominators(root, args):
    """
    a / b + c / d and a, b, c, d in Z  ->  a' / e + c' / e
    """
    scope, denom = args[::3]

    for fraction in args[1:3]:
        n, d = fraction
        mult = denom / d.value

        if mult != 1:
            if n.is_numeric():
                nom = L(n.value * mult)
            else:
                nom = L(mult) * n

            scope.replace(fraction, negate(nom / L(d.value * mult),
                                           fraction.negated))

    return scope.as_nary_node()


MESSAGES[equalize_denominators] = \
        _('Equalize the denominators of divisions' ' {2} and {3} to {4}.')


def constant_to_fraction(root, args):
    """
    a / b + c and a, b, c in Z  ->  a / b + b / b * c  # =>* (a + bc) / b
    """
    scope, ab, c = args
    b = ab[1]
    scope.replace(c, b / b * c)

    return scope.as_nary_node()


MESSAGES[constant_to_fraction] = \
        _('Rewrite constant {3} to a fraction to be able to add it to {2}.')


def match_multiply_fractions(node):
    """
    a / b * (c / d)  ->  ac / (bd)
    a / b * c and (c in Z or eval(a / b) not in Z)  ->  ac / b
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)
    fractions, others = partition(lambda n: n.is_op(OP_DIV), scope)
    numerics = filter(is_numeric_node, others)

    for ab, cd in combinations(fractions, 2):
        p.append(P(node, multiply_fractions, (scope, ab, cd)))

    for ab, c in product(fractions, others):
        a, b = ab

        #if (a.is_numeric() and c.is_numeric()) or \
        #        (a == 1 and evals_to_numeric(b)):
        if c.is_numeric() or not evals_to_numeric(ab):
            p.append(P(node, multiply_with_fraction, (scope, ab, c)))

    return p


def multiply_fractions(root, args):
    """
    a / b * (c / d)  ->  ac / (bd)
    """
    scope, ab, cd = args
    a, b = ab
    c, d = cd

    scope.replace(ab, (a * c / (b * d)).negate(ab.negated + cd.negated))
    scope.remove(cd)

    return scope.as_nary_node()


MESSAGES[multiply_fractions] = _('Multiply fractions {2} and {3}.')


def multiply_with_fraction(root, args):
    """
    a / b * c and a, c in Z or a == 1  ->  ac / b
    """
    scope, ab, c = args
    a, b = ab

    scope.replace(ab, (a * c / b).negate(ab.negated))
    scope.remove(c)

    return scope.as_nary_node()


MESSAGES[multiply_with_fraction] = \
        _('Multiply {3} with the nominator of fraction {2}.')


def match_divide_fractions(node):
    """
    Reduce divisions of fractions to a single fraction.

    Examples:
    a / b / c        ->  a / (bc)
    a / (b / c)      ->  ac / b

    Note that:
    a / b / (c / d)  ->*  ad / bd  # chain test!
    """
    assert node.is_op(OP_DIV)

    nom, denom = node
    p = []

    if nom.is_op(OP_DIV):
        p.append(P(node, divide_fraction, tuple(nom) + (denom,)))

    if denom.is_op(OP_DIV):
        p.append(P(node, divide_by_fraction, (nom,) + tuple(denom)))

    return p


def divide_fraction(root, args):
    """
    a / b / c  ->  a / (bc)
    """
    (a, b), c = root

    return (a / (b * c)).negate(root.negated)


MESSAGES[divide_fraction] = _('Move {3} to denominator of fraction {1} / {2}.')


def divide_by_fraction(root, args):
    """
    a / (b / c)  ->  ac / b
    """
    a, bc = root
    b, c = bc

    return (a * c / b).negate(root.negated + bc.negated)


MESSAGES[divide_by_fraction] = \
        _('Move {3} to nominator of fraction {1} / {2}.')


def fraction_scopes(node):
    """
    Get the multiplication scopes of the nominator and denominator of a
    fraction.
    """
    assert node.is_op(OP_DIV)

    nominator, denominator = node

    if nominator.is_op(OP_MUL):
        n_scope = Scope(nominator)
    else:
        n_scope = Scope(N(OP_MUL, nominator))

    if denominator.is_op(OP_MUL):
        d_scope = Scope(denominator)
    else:
        d_scope = Scope(N(OP_MUL, denominator))

    return n_scope, d_scope


def is_power_combination(a, b):
    """
    Check if two nodes are powers that can be combined in a fraction, for
    example:

    a and a^2
    a^2 and a^2
    a^2 and a
    """
    if a.is_power():
        a = a[0]

    if b.is_power():
        b = b[0]

    return a == b


def match_extract_fraction_terms(node):
    """
    Divide nominator and denominator by the same part.

    Examples:
    a ^ b * c / (a ^ d * e)  ->  a ^ b / a ^ d * (c / e)

    #If the same root appears in both nominator and denominator, extract it so
    #that it can be reduced to a single power by power division rules.
    #a ^ p * b / a ^ q  ->  a ^ p / a ^ q * b / 1
    #a ^ p * b / a      ->  a ^ p / a * b / 1
    #a * b / a ^ q      ->  a / a ^ q * b / 1
    """
    # TODO: ac / b  ->  a / b * c
    assert node.is_op(OP_DIV)

    nominator, denominator = node
    n_scope, d_scope = fraction_scopes(node)
    p = []

    if len(n_scope) == 1 and len(d_scope) == 1:
        return p

    # Look for matching parts in scopes
    for n, d in product(n_scope, d_scope):
        if is_power_combination(n, d):
            p.append(P(node, extract_fraction_terms, (n_scope, d_scope, n, d)))

    return p


def extract_fraction_terms(root, args):
    """
    ab / a                   ->  a / a * (b / 1)
    a / (ba)                 ->  a / a * (1 / b)
    a * c / (ae)             ->  a / a * (c / e)
    a ^ b * c / (a ^ d * e)  ->  a ^ b / a ^ d * (c / e)
    """
    n_scope, d_scope, n, d = args

    if len(n_scope) == 1:
        n_scope.replace(n, L(1))
    else:
        n_scope.remove(n)

    if len(d_scope) == 1:
        d_scope.replace(d, L(1))
    else:
        d_scope.remove(d)

    return n / d * (n_scope.as_nary_node() / d_scope.as_nary_node())


MESSAGES[extract_fraction_terms] = _('Extract {3} / {4} from fraction {0}.')
