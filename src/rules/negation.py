from ..node import OP_NEG, OP_ADD, OP_MUL, get_scope, nary_node
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

    if not val.is_leaf():
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

    print 'negate_group:', node, map(str, scope)

    # Negate each group
    for i, n in enumerate(scope):
        scope[i] = -n

    print nary_node('+', scope)
    return nary_node('+', scope)


MESSAGES[negate_group] = _('Apply negation to the subexpression {1[0]}.')


def double_negation(root, args):
    """
    --a  ->  a
    """
    node = args[0]

    return node[0][0]


MESSAGES[double_negation] = _('Remove double negation in {1}.')
