import unittest
from src.node import ExpressionNode
from src.parser import Parser
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


def rewrite(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp, '@'])


class RulesTestCase(unittest.TestCase):

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
                                          str(rewrite_chain[i+1]))
        except AssertionError:  # pragma: nocover
            print 'rewrite failed: "%s"  ->  "%s"' \
                    % (str(exp), str(rewrite_chain[i+1]))
            print 'rewrite chain index: %d' % i
            print 'rewrite chain: ---'

            for i, c in enumerate(rewrite_chain):
                print '%2d  %s' % (i, str(c))

            print '-' * 30

            raise
