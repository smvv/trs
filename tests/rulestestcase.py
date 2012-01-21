import unittest
from src.node import ExpressionNode
from src.parser import Parser
from tests.parser import ParserWrapper


def tree(exp, **kwargs):
    return ParserWrapper(Parser, **kwargs).run([exp])


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
