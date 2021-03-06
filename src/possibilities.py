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
from node import TYPE_OPERATOR, OP_MUL, Scope
import re


# Each rule will append its hint message to the following dictionary. The
# function pointer to the apply function of the rule is used as key. The
# corresponding value is a string, which will be used to produce the hint
# message. The string will be processed using string.format().
MESSAGES = {}


class Possibility(object):
    def __init__(self, root, handler, args=()):
        self.root = root
        self.handler = handler
        self.args = args

    def __str__(self):
        if self.handler in MESSAGES:
            msg = MESSAGES[self.handler]

            if callable(msg):
                msg = msg(self.root, self.args)

            # Surround math notation with backticks. If there are any backticks
            # already, do not add additional backticks. The add_backticks
            # lambda is necessary otherwise because \1 and \2 are not matched
            # both at the same time.
            add_backticks = lambda x: '`%s`' % ''.join(x.groups(''))
            msg = re.sub('`([^`]*)`|(\(?{[^. ]+)', add_backticks, msg)

            return msg.format(self.root, *self.args)

        return repr(self)

    def __repr__(self):
        return '<Possibility root="%s" handler=%s args=%s>' \
                % (self.root, self.handler.func_name, self.args)

    def __eq__(self, other):
        """
        Use node hash comparison when comparing to other Possibility to assert
        that its is the same object as in this one.
        """
        return self.handler == other.handler \
               and hash(self.root) == hash(other.root) \
               and self.args == other.args


def find_parent_node(root, child):
    nodes = [root]

    while nodes:
        node = nodes.pop()

        while node:
            if node.type != TYPE_OPERATOR:
                break

            if child in node:
                return node

            if len(node) > 1:
                nodes.append(node[1])

            node = node[0]


def flatten_mult(node):
    if node.is_leaf:
        return node

    if node.is_op(OP_MUL):
        scope = Scope(node)
        scope.nodes = map(flatten_mult, scope)
        return scope.as_nary_node()

    node.nodes = map(flatten_mult, node)

    return node


def apply_suggestion(root, suggestion):
    # TODO: clone the root node before modifying. After deep copying the root
    # node, the subtree_map cannot be used since the hash() of each node in the
    # deep copied root node has changed.
    #root = root.clone()

    subtree = suggestion.handler(suggestion.root, suggestion.args)
    parent_node = find_parent_node(root, suggestion.root)

    # There is either a parent node or the subtree is the root node.
    # FIXME: FAIL: test_diagnostic_test_application in tests/test_b1_ch08.py
    #try:
    #    assert bool(parent_node) != (subtree == root)
    #except:
    #    print 'parent_node: %s' % (str(parent_node))
    #    print 'subtree: %s == %s' % (str(subtree), str(root))
    #    raise

    if parent_node:
        parent_node.substitute(suggestion.root, subtree)
    else:
        root = subtree

    return flatten_mult(root)
