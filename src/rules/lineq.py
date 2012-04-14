from .utils import find_variable, evals_to_numeric
from ..node import ExpressionLeaf as L, Scope, OP_EQ, OP_ADD, OP_MUL, OP_DIV, \
        eq, OP_ABS
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_move_term(node):
    """
    Perform the same action on both sides of the equation such that variable
    terms are moved to the left, and constants (in relation to the variable
    that is being solved) are brought to the right side of the equation.
    If the variable is only present on the right side of the equation, swap the
    sides first.

    # Swap
    a = b * x  ->  b * x = a
    # Subtraction
    x + a = b  ->  x + a - a = b - a
    a = b + x  ->  a - x = b + x - x  # =>*  x = b / a
    # Division
    x * a = b  ->  x * a / a = b / a  # =>*  x = b / a
    # Multiplication
    x / a = b  ->  x / a * a = b * a  # =>*  x = a * b
    a / x = b  ->  a / x * x = b * x  # =>*  x = a / b
    -x = b     ->  -x * -1 = b * -1   # =>*  x = -b

    # Absolute value
    |f(x)| = c and eval(c) in Z  ->  f(x) = c vv f(x) = -c
    """
    assert node.is_op(OP_EQ)

    x = find_variable(node)
    left, right = node
    p = []

    if not left.contains(x):
        # Swap the left and right side if only the right side contains x
        if right.contains(x):
            p.append(P(node, swap_sides))

        return p

    # Bring terms without x to the right
    if left.is_op(OP_ADD):
        for n in Scope(left):
            if not n.contains(x):
                p.append(P(node, subtract_term, (n,)))

    # Bring terms with x to the left
    if right.is_op(OP_ADD):
        for n in Scope(right):
            if n.contains(x):
                p.append(P(node, subtract_term, (n,)))

    # Divide both sides by a constant to 'free' x
    if left.is_op(OP_MUL):
        for n in Scope(left):
            if not n.contains(x):
                p.append(P(node, divide_term, (n,)))

    # Multiply both sides by the denominator to move x out of the division
    if left.is_op(OP_DIV):
        p.append(P(node, multiply_term, (left[1],)))

    # Remove any negation from the left side of the equation
    if left.negated:
        p.append(P(node, multiply_term, (-L(1),)))

    # Split absolute equations into two separate, non-absolute equations
    if left.is_op(OP_ABS) and evals_to_numeric(right):
        p.append(P(node, split_absolute_equation))

    return p


def swap_sides(root, args):
    """
    a = bx  ->  bx = a
    """
    left, right = root

    return eq(right, left)


MESSAGES[swap_sides] = _('Swap the left and right side of the equation so ' \
        'that the variable is on the left side.')


def subtract_term(root, args):
    """
    x + a = b  ->  x + a - a = b - a
    a = b + x  ->  a - x = b + x - x
    """
    left, right = root
    term = args[0]

    return eq(left - term, right - term)


MESSAGES[subtract_term] = _('Subtract {1} from both sides of the equation.')


def divide_term(root, args):
    """
    x * a = b  ->  x * a / a = b / a  # =>*  x = b / a
    """
    left, right = root
    term = args[0]

    return eq(left / term, right / term)


MESSAGES[divide_term] = _('Divide both sides of the equation by {1}.')


def multiply_term(root, args):
    """
    x / a = b  ->  x / a * a = b * a  # =>*  x = a * b
    a / x = b  ->  a / x * x = b * x  # =>*  x = a / b
    """
    left, right = root
    term = args[0]

    return eq(left * term, right * term)


MESSAGES[multiply_term] = _('Multiply both sides of the equation with {1}.')


def split_absolute_equation(root, args):
    """
    |f(x)| = c and eval(c) in Z  ->  f(x) = c vv f(x) = -c
    """
    (f,), c = root

    return eq(f, c) | eq(f, -c)


MESSAGES[split_absolute_equation] = _('Split absolute equation {0} into a ' \
                                      'negative and a positive equation.')
