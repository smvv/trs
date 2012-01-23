from itertools import combinations

from ..node import ExpressionNode as Node, ExpressionLeaf as Leaf, Scope, \
        OP_ADD, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_combine_groups(node):
    """
    Match possible combinations of groups of expressions using non-strict
    equivalence.

    Examples:
    a + a     ->  2a
    a + 2a    ->  3a
    ab + ab   ->  2ab
    ab + 2ab  ->  3ab
    ab + ba   ->  2ab
    """
    # TODO: handle OP_NEG nodes
    assert node.is_op(OP_ADD)

    p = []
    groups = []

    for n in Scope(node):
        groups.append((1, n, n))

        # Each number multiplication yields a group, multiple occurences of
        # the same group can be replaced by a single one
        if n.is_op(OP_MUL):
            scope = Scope(n)
            l = len(scope)

            for i, sub_node in enumerate(scope):
                if sub_node.is_numeric():
                    others = [scope[j] for j in range(i) + range(i + 1, l)]
                    g = others[0] if len(others) == 1 else Node('*', *others)
                    groups.append((sub_node, g, n))

    #print [map(str, group) for group in groups]
    for g0, g1 in combinations(groups, 2):
        if g0[1].equals(g1[1]):
            #print type(g0[1]), str(g0[1]), 'equals', type(g1[1]), str(g1[1])
            p.append(P(node, combine_groups, g0 + g1))

    return p


def combine_groups(root, args):
    c0, g0, n0, c1, g1, n1 = args

    scope = Scope(root)

    if not isinstance(c0, Leaf):
        c0 = Leaf(c0)

    # Replace the left node with the new expression
    scope.remove(n0, (c0 + c1) * g0)

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[combine_groups] = \
        _('Group "{2}" is multiplied by {1} and {4}, combine them.')
