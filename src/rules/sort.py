from ..node import Scope, OP_MUL
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_sort_multiplicants(node):
    """
    Sort multiplicant factors by swapping
    x * 2  ->  2x
    """
    assert node.is_op(OP_MUL)

    p = []
    scope = Scope(node)

    for i, n in enumerate(scope[1:]):
        left_nb = scope[i]

        if n.is_numeric() and not left_nb.is_numeric():
            p.append(P(node, move_constant, (scope, n, left_nb)))

    return p


def move_constant(root, args):
    scope, constant, destination = args

    scope.replace(destination, constant * destination)
    scope.remove(constant)

    return scope.as_nary_node()


MESSAGES[move_constant] = \
        _('Move constant {2} to the left of the multiplication {0}.')
