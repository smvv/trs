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
import unittest
import doctest

from src.node import ExpressionNode
from src.parser import Parser
from src.validation import validate, VALIDATE_SUCCESS, \
        VALIDATE_FAILURE, VALIDATE_NOPROGRESS
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


def rewrite(exp, **kwargs):
    wrapper = ParserWrapper(Parser, **kwargs)
    wrapper.run([exp])

    return wrapper.parser.rewrite(check_implicit=False)


class RulesTestCase(unittest.TestCase):

    def assertDoctests(self, module):
        self.assertEqual(doctest.testmod(m=module)[0], 0,
                         'There are failed doctests.')

    def assertEqualPos(self, possibilities, expected):
        self.assertEqual(len(possibilities), len(expected))

        for p, e in zip(possibilities, expected):
            self.assertEqual(p.root, e.root)

            if p.args == None:  # pragma: nocover
                self.assertIsNone(e.args)
            elif e.args == None:  # pragma: nocover
                self.assertIsNone(p.args)
            else:
                for pair in zip(p.args, e.args):
                    self.assertEqual(*pair)

            self.assertEqual(p, e)

    def assertEqualNodes(self, a, b):
        if not isinstance(a, ExpressionNode):
            return self.assertEqual(a, b)

        self.assertIsInstance(b, ExpressionNode)
        self.assertEqual(a.op, b.op)

        for ca, cb in zip(a, b):
            self.assertEqualNodes(ca, cb)

    def assertRewrite(self, rewrite_chain):
        try:
            for i, exp in enumerate(rewrite_chain[:-1]):
                self.assertMultiLineEqual(str(rewrite(exp)),
                                          str(rewrite_chain[i + 1]))
        except AssertionError as e:  # pragma: nocover
            msg = e.args[0]

            msg += '-' * 30 + '\n'

            msg += 'rewrite failed: "%s"  ->  "%s"\n' \
                         % (str(exp), str(rewrite_chain[i + 1]))

            msg += 'rewrite chain: ---\n'

            chain = []

            for j, c in enumerate(rewrite_chain):
                if i == j:
                    chain.append('%2d  %s   <-- error' % (j, str(c)))
                else:
                    chain.append('%2d  %s' % (j, str(c)))

            e.message = msg + '\n'.join(chain)
            e.args = (e.message,) + e.args[1:]

            raise

    def assertValidateSuccess(self, a, b):
        self.assertEqual(validate(a, b), VALIDATE_SUCCESS,
                         'Validation failed: %s !=> %s' % (a, b))

    def assertValidateFailure(self, a, b):
        self.assertEqual(validate(a, b), VALIDATE_FAILURE,
                         'Validation dit not fail: %s => %s' % (a, b))

    def assertValidateNoprogress(self, a, b):
        self.assertEqual(validate(a, b), VALIDATE_NOPROGRESS, 'Validation '
                'did detect progress or failed for %s => %s' % (a, b))
