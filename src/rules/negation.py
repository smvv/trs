from ..node import get_scope, nary_node, OP_ADD, OP_MUL, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_negate_group(node):
    """
    --a                 ->  a
    -(a * ... * -b)     ->  ab
    -(a + b + ... + z)  ->  -a + -b + ... + -z
    """
    assert node.negated

    if node.negated == 2:
        # --a
        return [P(node, double_negation, (node,))]

    if not node.is_leaf:
        scope = get_scope(node)

        if node.is_op(OP_MUL) and any(map(lambda n: n.negated, scope)):
            # -(-a)b
            return [P(node, negate_group, (node, scope))]

        if node.is_op(OP_ADD):
            # -(ab + c)   ->  -ab - c
            # -(-ab + c)  ->  ab - c
            return [P(node, negate_polynome, (node, scope))]

    return []


def negate_group(root, args):
    """
    -(a * -3c)       ->  a * 3c
    -(a * ... * -b)  ->  ab
    """
    node, scope = args

    for i, n in enumerate(scope):
        if n.negated:
            scope[i] = n.reduce_negation()

    return nary_node('*', scope).reduce_negation()


MESSAGES[negate_group] = _('Apply negation to the polynome {1[0]}.')


def negate_polynome(root, args):
    """
    -(-ab + ... + c)  ->  --ab + ... + -c
    """
    node, scope = args

    # Negate each group
    for i, n in enumerate(scope):
        scope[i] = -n

    return nary_node('+', scope)


MESSAGES[negate_polynome] = _('Apply negation to the subexpression {1[0]}.')


def double_negation(root, args):
    """
    --a  ->  a
    """
    return negate(args[0], args[0].negated - 2)


MESSAGES[double_negation] = _('Remove double negation in {1}.')


def match_negated_division(node):
    """
    -a / -b  ->  a / b
    """
    assert node.is_op(OP_DIV)

    a, b = node

    if a.negated and b.negated:
        return [P(node, double_negated_division, (node,))]
    elif a.negated:
        return [P(node, single_negated_division, (a[0], b))]
    elif b.negated:
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


# TODO: negated multiplication: -a * -b = ab
