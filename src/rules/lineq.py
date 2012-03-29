from .utils import find_variable
from ..node import Scope, OP_EQ, OP_ADD, OP_MUL, eq
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_subtract_addition_term(node):
    """
    x + a = b   ->  x + a - a = b - a
    x = b + cx  ->  x + - cx = b + cx - cx
    """
    assert node.is_op(OP_EQ)

    x = find_variable(node)
    p = []
    left, right = node

    if left.is_op(OP_ADD):
        scope = Scope(left)

        for n in scope:
            # Bring terms without x to the right
            if not n.contains(x):
                p.append(P(node, subtract_addition_term, (n,)))

    if right.is_op(OP_ADD):
        scope = Scope(right)

        for n in scope:
            # Bring terms with x to the left
            if n.contains(x):
                p.append(P(node, subtract_addition_term, (n,)))

    return p


def subtract_addition_term(root, args):
    """
    x + a = b   ->  x + a - a = b - a
    x = b + cx  ->  x + - cx = b + cx - cx
    """
    left, right = root
    term = args[0]

    return eq(left - term, right - term)


MESSAGES[subtract_addition_term] = \
        _('Subtract {1} from both sides of the equation.')
