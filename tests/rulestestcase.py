import unittest
from src.node import ExpressionNode


class RulesTestCase(unittest.TestCase):

    def assertEqualPos(self, possibilities, expected):
        self.assertEqual(len(possibilities), len(expected))

        for p, e in zip(possibilities, expected):
            self.assertEqual(p.root, e.root)

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
