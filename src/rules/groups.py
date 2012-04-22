from itertools import combinations

from .utils import evals_to_numeric
from ..node import ExpressionLeaf as Leaf, Scope, OP_ADD, OP_MUL, nary_node, \
        negate
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
    assert node.is_op(OP_ADD)

    p = []
    groups = []
    scope = Scope(node)

    for n in scope:
        if not n.is_numeric():
            groups.append((Leaf(1), n, n, True))

        # Each number multiplication yields a group, multiple occurences of
        # the same group can be replaced by a single one
        if n.is_op(OP_MUL):
            n_scope = Scope(n)
            l = len(n_scope)

            for i, sub_node in enumerate(n_scope):
                if evals_to_numeric(sub_node):
                    others = [n_scope[j] for j in range(i) + range(i + 1, l)]

                    if len(others) == 1:
                        g = others[0]
                    else:
                        g = nary_node(OP_MUL, others)

                    groups.append((sub_node, g, n, False))

    for (c0, g0, n0, root0), (c1, g1, n1, root1) in combinations(groups, 2):
        if not root0:
            c0 = c0.negate(n0.negated)

        if not root1:
            c1 = c1.negate(n1.negated)

        if g0.equals(g1):
            p.append(P(node, combine_groups, (scope, c0, g0, n0, c1, g1, n1)))
        elif g0.equals(g1, ignore_negation=True):
            # Move negations to constants
            c0 = c0.negate(g0.negated)
            c1 = c1.negate(g1.negated)
            g0 = negate(g0, 0)
            g1 = negate(g1, 0)

            p.append(P(node, combine_groups, (scope, c0, g0, n0, c1, g1, n1)))

    return p


def combine_groups(root, args):
    scope, c0, g0, n0, c1, g1, n1 = args

    # Replace the left node with the new expression
    scope.replace(n0, (c0 + c1) * g0)

    # Remove the right node
    scope.remove(n1)

    return scope.as_nary_node()


MESSAGES[combine_groups] = _('Combine occurences of {3}.')
