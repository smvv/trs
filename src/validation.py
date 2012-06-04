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
from parser import Parser
from possibilities import apply_suggestion
from strategy import find_possibilities
from tests.parser import ParserWrapper


def validate(exp, result):
    """
    Validate that exp =>* result.
    """
    parser = ParserWrapper(Parser)

    exp = parser.run([exp])
    result = parser.run([result])

    # Compare the simplified expressions first, in order to avoid the
    # computational intensive traversal of the possibilities tree.
    parser.set_root_node(exp)
    a = parser.rewrite_all()

    parser.set_root_node(result)
    b = parser.rewrite_all()

    if not a or not a.equals(b):
        return False

    # TODO: make sure cycles are avoided / eliminated using cycle detection.
    def traverse_preorder(node, result):
        if node.equals(result):
            return True

        for p in find_possibilities(node):
            # Clone the root node because it will be used in multiple
            # substitutions
            child = apply_suggestion(node.clone(), p)

            if traverse_preorder(child, result):
                return True

        return False

    return traverse_preorder(exp, result)
