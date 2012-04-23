import math

from .utils import dividers, is_prime
from ..node import ExpressionLeaf as Leaf, Scope, OP_SQRT, OP_MUL, sqrt
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def is_eliminateable_sqrt(n):
    if isinstance(n, int):
        return n > 3 and int(math.sqrt(n)) ** 2 == n

    if n.negated:
        return False

    if n.is_numeric():
        return is_eliminateable_sqrt(n.value)

    return n.is_power(2)


def match_reduce_sqrt(node):
    """
    sqrt(a ^ 2)  ->  a
    sqrt(a) and eval(sqrt(a)) in Z              ->  eval(sqrt(a))
    sqrt(a) and a == b ^ 2 * c with a,b,c in Z  ->  sqrt(eval(b ^ 2) * c)
    sqrt(ab)     ->  sqrt(a)sqrt(b)
    """
    assert node.is_op(OP_SQRT)

    exp = node[0]

    if exp.negated:
        return []

    if exp.is_power(2):
        return [P(node, quadrant_sqrt)]

    if exp.is_numeric():
        reduced = int(math.sqrt(exp.value))

        if reduced ** 2 == exp.value:
            return [P(node, constant_sqrt, (reduced,))]

        div = filter(is_eliminateable_sqrt, dividers(exp.value))
        div.sort(lambda a, b: cmp(is_prime(b), is_prime(a)))

        return [P(node, split_dividers, (m, exp.value / m)) for m in div]

    if exp.is_op(OP_MUL):
        scope = Scope(exp)
        p = []

        for n in scope:
            if is_eliminateable_sqrt(n):
                p.append(P(node, extract_sqrt_mult_priority, (scope, n)))
            else:
                p.append(P(node, extract_sqrt_multiplicant, (scope, n)))

        return p

    return []


def quadrant_sqrt(root, args):
    """
    sqrt(a ^ 2)  ->  a
    """
    return root[0][0].negate(root.negated)


MESSAGES[quadrant_sqrt] = \
        _('The square root of a quadrant reduces to the raised root.')


def constant_sqrt(root, args):
    """
    sqrt(a) and eval(sqrt(a)) in Z  ->  eval(sqrt(a))
    """
    return Leaf(args[0]).negate(root.negated)


MESSAGES[constant_sqrt] = \
        _('The square root of {0[0]} is {1}.')


def split_dividers(root, args):
    """
    sqrt(a) and b * c = a with a,b,c in Z  ->  sqrt(a * b)
    """
    b, c = args

    return sqrt(Leaf(b) * c)


MESSAGES[split_dividers] = _('Write {0[0]} as {1} * {2} to so that {1} can ' \
        'be brought outside of the square root.')


def extract_sqrt_multiplicant(root, args):
    """
    sqrt(ab)     ->  sqrt(a)sqrt(b)
    """
    scope, a = args
    scope.remove(a)

    return (sqrt(a) * sqrt(scope.as_nary_node())).negate(root.negated)


MESSAGES[extract_sqrt_multiplicant] = _('Extract {2} from {0}.')


def extract_sqrt_mult_priority(root, args):
    """
    sqrt(ab) and sqrt(a) in Z  ->  sqrt(a)sqrt(b)
    """
    return extract_sqrt_multiplicant(root, args)


MESSAGES[extract_sqrt_mult_priority] = MESSAGES[extract_sqrt_multiplicant]
