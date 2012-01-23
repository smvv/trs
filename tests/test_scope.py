import unittest

from src.scope import Scope
from tests.rulestestcase import RulesTestCase, tree


class TestScope(RulesTestCase):

    def setUp(self):
        self.n, self.f = tree('a + b + cd,f')
        (self.a, self.b), self.cd = self.n
        self.c, self.d = self.cd
        self.scope = Scope(self.n)

    def test___init__(self):
        self.assertEqual(self.scope.node, self.n)
        self.assertEqual(self.scope.nodes, [self.a, self.b, self.cd])

    def test_remove_leaf(self):
        self.scope.remove(self.b)
        self.assertEqual(self.scope.nodes, [self.a, self.cd])

    def test_remove_node(self):
        self.scope.remove(self.cd)
        self.assertEqual(self.scope.nodes, [self.a, self.b])

    def test_remove_replace(self):
        self.scope.remove(self.cd, self.f)
        self.assertEqual(self.scope.nodes, [self.a, self.b, self.f])

    def test_remove_error(self):
        with self.assertRaises(ValueError):
            self.scope.remove(self.f)

    def test_as_nary_node(self):
        self.assertEqualNodes(self.scope.as_nary_node(), self.n)
