from ..node import Scope, OP_ADD, OP_MUL, OP_DIV
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_negated_factor(node):
    """
    This rule assures that negations in the scope of a multiplication are
    brought to the most left node in the multiplication's scope.

    Example:
    a * -b  ->  -ab
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)

    # FIXME: The negation that is brought outside is assigned to the first
    # element in the scope during the next parsing step:
    # -ab -> -(ab), but -(ab) is printed as -ab
    for factor in scope[1:]:
        if factor.negated:
            p.append(P(node, negated_factor, (scope, factor)))

    return p


def negated_factor(root, args):
    """
    a * -b  ->  -ab
    """
    scope, factor = args
    scope[0] = -scope[0]
    scope.replace(factor, +factor)

    return scope.as_nary_node()


MESSAGES[negated_factor] = \
        _('Bring negation of {2} to the outside of the multiplication.')


def match_negate_polynome(node):
    """
    --a       ->  a
    -(a + b)  ->  -a - b
    """
    #print 'match_negate_polynome:', node, node.negated
    assert node.negated, str(node.negated) + '; ' + str(node)

    p = []

    if node.negated == 2:
        # --a
        p.append(P(node, double_negation, ()))

    if node.is_op(OP_ADD):
        # -(a + b)  ->  -a - b
        p.append(P(node, negate_polynome, ()))

    return p


def double_negation(root, args):
    """
    --a  ->  a
    """
    return root.reduce_negation(2)


MESSAGES[double_negation] = _('Remove double negation in {0}.')


def negate_polynome(root, args):
    """
    -(a + b)  ->  -a - b
    """
    scope = Scope(root)

    # Negate each group
    for i, n in enumerate(scope):
        scope[i] = -n

    return +scope.as_nary_node()


MESSAGES[negate_polynome] = _('Apply negation to the polynome {0}.')


#def negate_group(root, args):
#    """
#    -(a * -3c)       ->  a * 3c
#    -(a * ... * -b)  ->  ab
#    """
#    node, scope = args
#
#    for i, n in enumerate(scope):
#        if n.negated:
#            scope[i] = n.reduce_negation()
#
#    return nary_node('*', scope).reduce_negation()
#
#
#MESSAGES[negate_polynome] = _('Apply negation to the subexpression {1[0]}.')


def match_negated_division(node):
    """
    -a / -b  ->  a / b
    """
    assert node.is_op(OP_DIV)

    a, b = node

    if a.negated and b.negated:
        return [P(node, double_negated_division, ())]
    elif b.negated:
        return [P(node, single_negated_division, (a, +b))]

    return []


def single_negated_division(root, args):
    """
    a / -b  ->  -a / b
    """
    a, b = args

    # FIXME: "-a/b" results in "-(a/b)", which will cause a loop.

    return -a / b


MESSAGES[single_negated_division] = \
        _('Bring negation outside of the division: -{1} / {2}.')


def double_negated_division(root, args):
    """
    -a / -b  ->  a / b
    """
    a, b = root

    return +a / +b


MESSAGES[double_negated_division] = \
        _('Eliminate top and bottom negation in {0}.')


# TODO: negated multiplication: -a * -b = ab
