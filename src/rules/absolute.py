# This file is part of TRS (http://math.kompiler.org)
#
# TRS is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# TRS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with TRS.  If not, see <http://www.gnu.org/licenses/>.
from .utils import evals_to_numeric
from ..node import OP_ABS, OP_SQRT, OP_MUL, OP_POW, Scope, absolute, sqrt
from ..possibilities import Possibility as P, MESSAGES
from ..translate import _


def match_factor_out_abs_term(node):
    """
    |-a|            ->  |a|
    |c| and c in Z  ->  eval(|c|)
    |sqrt a|        ->  sqrt |a|
    |ab|            ->  |a||b|
    |abc|           ->  |a||bc|
    |abc|           ->  |c||ab|
    |abc|           ->  |b||ac|
    |a ^ c| and eval(c) in Z  ->  |a| ^ c
    """
    assert node.is_op(OP_ABS)

    exp = node[0]

    if exp.negated:
        return [P(node, remove_absolute_negation)]

    if exp.is_numeric():
        return [P(node, absolute_numeric)]

    if exp.is_op(OP_MUL):
        scope = Scope(exp)

        return [P(node, factor_out_abs_term, (scope, n)) for n in scope]

    if exp.is_op(OP_SQRT):
        return [P(node, factor_out_abs_sqrt)]

    if exp.is_op(OP_POW) and evals_to_numeric(exp[1]):
        return [P(node, factor_out_abs_exponent)]

    return []


def remove_absolute_negation(root, args):
    """
    |-a|  ->  |a|
    """
    return absolute(+root[0]).negate(root.negated)


MESSAGES[remove_absolute_negation] =  \
        _('The absolute value of a negated expression is the expression.')


def absolute_numeric(root, args):
    """
    |c| and c in Z  ->  eval(|c|)
    """
    return root[0].negate(root.negated)


MESSAGES[absolute_numeric] = _('The absolute value of {0[0]} is {0[0]}.')


def factor_out_abs_term(root, args):
    """
    |ab|  ->  |a||b|
    """
    scope, a = args
    scope.remove(a)

    return (absolute(a) * absolute(scope.as_nary_node())).negate(root.negated)


MESSAGES[factor_out_abs_term] = _('Split the multplication in absolute ' \
        'value {0} into a multiplication of absolute values.')


def factor_out_abs_sqrt(root, args):
    """
    |sqrt a|  ->  sqrt|a|
    """
    return sqrt(absolute(root[0][0])).negate(root.negated)


MESSAGES[factor_out_abs_sqrt] = \
        _('Move the absolute value in {0} to the operand of the square root.')


def factor_out_abs_exponent(root, args):
    """
    |a ^ c| and eval(c) in Z  ->  |a| ^ c
    """
    a, c = root[0]

    return (absolute(a) ** c).negate(root.negated)


MESSAGES[factor_out_abs_exponent] = _('Factor out the exponent in {0}.')
