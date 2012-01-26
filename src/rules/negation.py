from ..node import get_scope, nary_node, OP_NEG, OP_ADD, OP_MUL, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_negate_group(node):
    """
    --a                 ->  a
    --ab                ->  ab
    -(-ab + c)          ->  --ab - c
    -(a + b + ... + z)  ->  -a + -b + ... + -z
    """
    assert node.is_op(OP_NEG)

    val = node[0]

    if val.is_op(OP_NEG):
        # --a
        return [P(node, double_negation, (node,))]

    if not val.is_leaf:
        scope = get_scope(val)

        if not any(map(lambda n: n.is_op(OP_NEG), scope)):
            return []

        if val.is_op(OP_MUL):
            # --ab
            return [P(node, negate_polynome, (node, scope))]

        elif val.is_op(OP_ADD):
            # -(ab + c)   ->  -ab - c
            # -(-ab + c)  ->  ab - c
            return [P(node, negate_group, (node, scope))]

    return []


def negate_polynome(root, args):
    """
    # -a * -3c  ->  a * 3c
    --a * 3c  ->  a * 3c
    --ab      ->  ab
    --abc     ->  abc
    """
    node, scope = args

    for i, n in enumerate(scope):
        # XXX: validate this property!
        if n.is_op(OP_NEG):
            scope[i] = n[0]
            return nary_node('*', scope)

    raise RuntimeError('No negation node found in scope.')


MESSAGES[negate_polynome] = _('Apply negation to the polynome {1[0]}.')


def negate_group(root, args):
    """
    -(-ab + ... + c)  ->  --ab + ... + -c
    """
    node, scope = args

    # Negate each group
    for i, n in enumerate(scope):
        scope[i] = -n

    return nary_node('+', scope)


MESSAGES[negate_group] = _('Apply negation to the subexpression {1[0]}.')


def double_negation(root, args):
    """
    --a  ->  a
    """
    node = args[0]

    return node[0][0]


MESSAGES[double_negation] = _('Remove double negation in {1}.')


def match_negated_division(node):
    """
    -a / -b  ->  a / b
    """
    assert node.is_op(OP_DIV)

    a, b = node
    a_neg = a.is_op(OP_NEG)
    b_neg = b.is_op(OP_NEG)

    if a_neg and b_neg:
        return [P(node, double_negated_division, (node,))]
    elif a_neg:
        return [P(node, single_negated_division, (a[0], b))]
    elif b_neg:
        return [P(node, single_negated_division, (a, b[0]))]

    return []


def single_negated_division(root, args):
    """
    -a / b  ->  -(a / b)
    a / -b  ->  -(a / b)
    """
    a, b = args

    # FIXME: "-a/b" results in "-(a/b)", which will cause a loop.

    return -(a / b)


MESSAGES[single_negated_division] = \
        _('Bring negation outside of the division: -({1} / {2}).')


def double_negated_division(root, args):
    """
    -a / -b  ->  a / b
    """
    a, b = root

    return a[0] / b[0]


MESSAGES[double_negated_division] = \
        _('Eliminate top and bottom negation in {1}.')
