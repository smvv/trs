from ..node import ExpressionNode as Node, OP_ADD
from .poly import match_combine_factors#, match_combine_parentheses


RULES = {
        OP_ADD: [match_combine_factors],
        #OP_MUL: [match_combine_parentheses],
        }
