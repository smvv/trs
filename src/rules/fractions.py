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
from itertools import combinations, product, ifilterfalse

from .utils import least_common_multiple, partition, is_numeric_node, \
        evals_to_numeric
from ..node import ExpressionNode as N, ExpressionLeaf as L, Scope, OP_DIV, \
        OP_ADD, OP_MUL, negate
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _
from .negation import negate_polynome


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
    return args[0].negate(root.negated)


MESSAGES[division_by_one] = _('Division by `1` yields the nominator.')


def division_of_zero(root, args):
    """
    0 / a  ->  0
    """
    return L(0, negated=root.negated)


MESSAGES[division_of_zero] = _('Division of `0` by {1} reduces to `0`.')


def division_by_self(root, args):
    """
    a / a  ->  1
    """
    return L(1, negated=root.negated)


MESSAGES[division_by_self] = _('Division of {1} by itself reduces to `1`.')


def match_add_fractions(node):
    """
    a / b + c / b and a, c in Z        ->  (a + c) / b
    a / b + c / d and a, b, c, d in Z  ->  a' / e + c' / e  # e = lcm(b, d)
                                                            # | e = b * d
    a / b + c and a, b, c in Z         ->  a / b + (bc) / b # =>* (a + bc) / b
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
        _('Equalize the denominators of divisions {2} and {3} to {4}.')


def constant_to_fraction(root, args):
    """
    a / b + c and a, b, c in Z  ->  a / b + (bc) / b  # =>* (a + bc) / b
    """
    scope, ab, c = args
    b = ab[1]
    scope.replace(c, b * c / b)

    return scope.as_nary_node()


MESSAGES[constant_to_fraction] = \
        _('Rewrite constant {3} to a fraction to be able to add it to {2}.')


def match_multiply_fractions(node):
    """
    a / b * c / d  ->  (ac) / (bd)
    a / b * c and (eval(c) in Z or eval(a / b) not in Z)  ->  (ac) / b
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)
    fractions, others = partition(lambda n: n.is_op(OP_DIV), scope)

    for ab, cd in combinations(fractions, 2):
        p.append(P(node, multiply_fractions, (scope, ab, cd)))

    for ab, c in product(fractions, others):
        if evals_to_numeric(c) or not evals_to_numeric(ab):
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
    a / b * c and (eval(c) in Z or eval(a / b) not in Z)  ->  (ac) / b
    """
    scope, ab, c = args
    a, b = ab

    if scope.index(ab) < scope.index(c):
        nominator = a * c
    else:
        nominator = c * a

    scope.replace(ab, negate(nominator / b, ab.negated))
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
    a / b / (c / d)  =>  ad / bd
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

    return negate(a / (b * c), root.negated)


MESSAGES[divide_fraction] = \
        _('Move {3} to denominator of fraction `{1} / {2}`.')


def divide_by_fraction(root, args):
    """
    a / (b / c)  ->  ac / b
    """
    a, bc = root
    b, c = bc

    return negate(a * c / b, root.negated + bc.negated)


MESSAGES[divide_by_fraction] = \
        _('Move {3} to the nominator of fraction `{1} / {2}`.')


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


def mult_scope(node):
    """
    Get the multiplication scope of a node that may or may no be a
    multiplication itself.
    """
    if node.is_op(OP_MUL):
        return Scope(node)

    return Scope(N(OP_MUL, node))


def remove_from_mult_scope(scope, node):
    if len(scope) == 1:
        scope.replace(node, L(1))
    else:
        scope.remove(node)

    return scope.as_nary_node()


def match_extract_fraction_terms(node):
    """
    Divide nominator and denominator by the same part. If the same root of a
    power appears in both nominator and denominator, also extract it so that it
    can be reduced to a single power by power division rules.

    Examples:
    ab / (ac)                ->  a / a * (c / e)          # =>* c / e
    a ^ b * c / (a ^ d * e)  ->  a ^ b / a ^ d * (c / e)  # -> a^(b - d)(c / e)

    ac / b and eval(c) not in Z and eval(a / b) in Z  ->  a / b * c
    """
    assert node.is_op(OP_DIV)

    n_scope, d_scope = map(mult_scope, node)
    p = []
    nominator, denominator = node

    # ac / b
    for n in ifilterfalse(evals_to_numeric, n_scope):
        a_scope = mult_scope(nominator)

        #a = remove_from_mult_scope(a_scope, n)
        if len(a_scope) == 1:
            a = L(1)
        else:
            a = a_scope.all_except(n)

        if evals_to_numeric(a / denominator):
            p.append(P(node, extract_nominator_term, (a, n)))

    if len(n_scope) == 1 and len(d_scope) == 1:
        return p

    # a ^ b * c / (a ^ d * e)
    for n, d in product(n_scope, d_scope):
        if n == d:
            handler = divide_fraction_by_term
        elif is_power_combination(n, d):
            handler = extract_fraction_terms
        else:
            continue  # pragma: nocover

        p.append(P(node, handler, (n_scope, d_scope, n, d)))

    return p


def extract_nominator_term(root, args):
    """
    ac / b and eval(c) not in Z and eval(a / b) in Z  ->  a / b * c
    """
    a, c = args

    return negate(a / root[1] * c, root.negated)


MESSAGES[extract_nominator_term] = \
        _('Extract {2} from the nominator of fraction {0}.')


def extract_fraction_terms(root, args):
    """
    a ^ b * c / (a ^ d * e)  ->  a ^ b / a ^ d * (c / e)
    """
    n_scope, d_scope, n, d = args
    div = n / d * (remove_from_mult_scope(n_scope, n) \
                   / remove_from_mult_scope(d_scope, d))

    return negate(div, root.negated)


MESSAGES[extract_fraction_terms] = _('Extract `{3} / {4}` from fraction {0}.')


def divide_fraction_by_term(root, args):
    """
    ab / a                   ->  b
    a / (ba)                 ->  1 / b
    a * c / (ae)             ->  c / e
    """
    n_scope, d_scope, n, d = args

    nom = remove_from_mult_scope(n_scope, n)
    d_scope.remove(d)

    if not len(d_scope):
        return negate(nom, root.negated)

    return negate(nom / d_scope.as_nary_node(), root.negated)


MESSAGES[divide_fraction_by_term] = \
        _('Divide nominator and denominator od {0} by {2}.')


def match_division_in_denominator(node):
    """
    a / (b / c + d)  ->  (ca) / (c(b / c + d))
    """
    assert node.is_op(OP_DIV)

    denom = node[1]

    if not denom.is_op(OP_ADD):
        return []

    return [P(node, multiply_with_term, (n[1],))
            for n in Scope(denom) if n.is_op(OP_DIV)]


def multiply_with_term(root, args):
    """
    a / (b / c + d)  ->  (ca) / (c(b / c + d))
    """
    c = args[0]
    nom, denom = root

    return negate(c * nom / (c * denom), root.negated)


MESSAGES[multiply_with_term] = \
        _('Multiply nominator and denominator of {0} with {1}.')


def match_combine_fractions(node):
    """
    a/b + c/d  ->  ad/(bd) + bc/(bd)  # ->  (ad + bc)/(bd)
    """
    assert node.is_op(OP_ADD)

    scope = Scope(node)
    fractions = [n for n in scope if n.is_op(OP_DIV)]
    p = []

    for left, right in combinations(fractions, 2):
        p.append(P(node, combine_fractions, (scope, left, right)))

    return p


def combine_fractions(root, args):
    """
    a/b + c/d  ->  ad/(bd) + bc/(bd)
    """
    scope, ab, cd = args
    (a, b), (c, d) = ab, cd
    a = negate(a, ab.negated)
    d = negate(d, cd.negated)

    scope.replace(ab, a * d / (b * d) + b * c / (b * d))
    scope.remove(cd)

    return scope.as_nary_node()


MESSAGES[combine_fractions] = _('Combine fraction {2} and {3}.')


def match_remove_division_negation(node):
    """
    -a / (-b + c)  -> a / (--b - c)
    """
    assert node.is_op(OP_DIV)
    nom, denom = node

    if node.negated:
        if nom.is_op(OP_ADD) and any([n.negated for n in Scope(nom)]):
            return [P(node, remove_division_negation, (True, nom))]

        if denom.is_op(OP_ADD) and any([n.negated for n in Scope(denom)]):
            return [P(node, remove_division_negation, (False, denom))]

    return []


def remove_division_negation(root, args):
    """
    -a / (-b + c)  -> a / (--b - c)
    """
    nom, denom = root

    if args[0]:
        nom = negate_polynome(nom, ())
    else:
        denom = negate_polynome(denom, ())

    return negate(nom / denom, root.negated - 1)


MESSAGES[remove_division_negation] = \
        _('Move negation from fraction {0} to polynome {2}.')


def match_fraction_in_division(node):
    """
    (1 / a * b) / c  ->  b / (ac)
    c / (1 / a * b)  ->  (ac) / b
    """
    assert node.is_op(OP_DIV)
    nom, denom = node
    p = []

    if nom.is_op(OP_MUL):
        scope = Scope(nom)

        for n in scope:
            if n.is_op(OP_DIV) and n[0] == 1:
                p.append(P(node, fraction_in_division, (True, scope, n)))

    if denom.is_op(OP_MUL):
        scope = Scope(denom)

        for n in scope:
            if n.is_op(OP_DIV) and n[0] == 1:
                p.append(P(node, fraction_in_division, (False, scope, n)))

    return p


def fraction_in_division(root, args):
    """
    (1 / a * b) / c  ->  b / (ac)
    c / (1 / a * b)  ->  (ac) / b
    """
    is_nominator, scope, fraction = args
    nom, denom = root

    if fraction.negated:
        scope.replace(fraction, fraction[0].negate(fraction.negated))
    else:
        scope.remove(fraction)

    if is_nominator:
        nom = scope.as_nary_node()
        denom = fraction[1] * denom
    else:
        nom = fraction[1] * nom
        denom = scope.as_nary_node()

    return negate(nom / denom, root.negated)


MESSAGES[fraction_in_division] = \
        _('Multiply both sides of fraction {0} with {3[1]}.')
