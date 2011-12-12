from ..node import ExpressionNode as Node


def nary_node(operator, scope):
    """
    Create a binary expression tree for an n-ary operator. Takes the operator
    and a list of expression nodes as arguments.
    """
    return scope[0] if len(scope) == 1 \
           else Node(operator, nary_node(operator, scope[:-1]), scope[-1])
