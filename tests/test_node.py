from src.node import ExpressionNode as N, ExpressionLeaf as L, Scope, \
        nary_node, get_scope, OP_ADD
from tests.rulestestcase import RulesTestCase, tree


class TestNode(RulesTestCase):

    def setUp(self):
        self.l = [L(1), N('*', L(2), L(3)), L(4), L(5)]
        self.n, self.f = tree('a + b + cd,f')
        (self.a, self.b), self.cd = self.n
        self.c, self.d = self.cd
        self.scope = Scope(self.n)

    def test___lt__(self):
        self.assertTrue(L(1) < L(2))
        self.assertFalse(L(1) < L(1))
        self.assertFalse(L(2) < L(1))

        self.assertTrue(L(2) < N('+', L(1), L(2)))
        self.assertFalse(N('+', L(1), L(2)) < L(1))

        self.assertTrue(N('^', L('a'), L(2)) < N('^', L('a'), L(3)))
        self.assertTrue(N('^', L(2), L('a')) < N('^', L(3), L('a')))
        self.assertTrue(N('*', L(2), N('^', L('a'), L('b')))
                        < N('*', L(3), N('^', L('a'), L('b'))))
        self.assertFalse(N('^', L('a'), L(3)) < N('^', L('a'), L(2)))

    def test_is_op(self):
        self.assertTrue(N('+', *self.l[:2]).is_op(OP_ADD))
        self.assertFalse(N('-', *self.l[:2]).is_op(OP_ADD))

    def test_is_leaf(self):
        self.assertTrue(L(2).is_leaf)
        self.assertFalse(N('+', *self.l[:2]).is_leaf)

    def test_is_power(self):
        self.assertTrue(N('^', *self.l[:2]).is_power())
        self.assertFalse(N('+', *self.l[:2]).is_power())

    def test_is_nary(self):
        self.assertTrue(N('+', *self.l[:2]).is_nary())
        self.assertTrue(N('-', *self.l[:2]).is_nary())
        self.assertTrue(N('*', *self.l[:2]).is_nary())
        self.assertFalse(N('^', *self.l[:2]).is_nary())

    def test_is_identifier(self):
        self.assertTrue(L('a').is_identifier())
        self.assertFalse(L(1).is_identifier())

    def test_is_int(self):
        self.assertTrue(L(1).is_int())
        self.assertFalse(L(1.5).is_int())
        self.assertFalse(L('a').is_int())

    def test_is_float(self):
        self.assertTrue(L(1.5).is_float())
        self.assertFalse(L(1).is_float())
        self.assertFalse(L('a').is_float())

    def test_is_numeric(self):
        self.assertTrue(L(1).is_numeric())
        self.assertTrue(L(1.5).is_numeric())
        self.assertFalse(L('a').is_numeric())

    def test_extract_polynome_properties_identifier(self):
        self.assertEqual(L('a').extract_polynome_properties(),
                         (L(1), L('a'), L(1)))

    def test_extract_polynome_properties_None(self):
        self.assertIsNone(N('+').extract_polynome_properties())

    def test_extract_polynome_properties_power(self):
        power = N('^', L('a'), L(2))
        self.assertEqual(power.extract_polynome_properties(),
                         (L(1), L('a'), L(2)))

    def test_extract_polynome_properties_coefficient_exponent_int(self):
        times = N('*', L(3), N('^', L('a'), L(2)))
        self.assertEqual(times.extract_polynome_properties(),
                         (L(3), L('a'), L(2)))

    def test_extract_polynome_properties_coefficient_exponent_id(self):
        times = N('*', L(3), N('^', L('a'), L('b')))
        self.assertEqual(times.extract_polynome_properties(),
                         (L(3), L('a'), L('b')))

    def test_get_scope_binary(self):
        plus = N('+', *self.l[:2])
        self.assertEqual(get_scope(plus), self.l[:2])

    def test_get_scope_nested_left(self):
        plus = N('+', N('+', *self.l[:2]), self.l[2])
        self.assertEqual(get_scope(plus), self.l[:3])

    def test_get_scope_nested_right(self):
        plus = N('+', self.l[0], N('+', *self.l[1:3]))
        self.assertEqual(get_scope(plus), self.l[:3])

    def test_get_scope_nested_deep(self):
        plus = N('+', N('+', N('+', *self.l[:2]), self.l[2]), self.l[3])
        self.assertEqual(get_scope(plus), self.l)

    def test_equals_node_leaf(self):
        a, b = plus = tree('a + b')

        self.assertFalse(a.equals(plus))
        self.assertFalse(plus.equals(a))

    def test_equals_other_op(self):
        plus, mul = tree('a + b, a * b')

        self.assertFalse(plus.equals(mul))

    def test_equals_add(self):
        p0, p1, p2, p3 = tree('a + b,a + b,b + a, a + c')

        self.assertTrue(p0.equals(p1))
        self.assertTrue(p0.equals(p2))
        self.assertFalse(p0.equals(p3))
        self.assertFalse(p2.equals(p3))

    def test_equals_mul(self):
        m0, m1, m2, m3 = tree('a * b,a * b,b * a, a * c')

        self.assertTrue(m0.equals(m1))
        self.assertTrue(m0.equals(m2))
        self.assertFalse(m0.equals(m3))
        self.assertFalse(m2.equals(m3))

    def test_equals_nary(self):
        p0, p1, p2, p3, p4 = \
                tree('a + b + c,a + c + b,b + a + c,b + c + a,a + b + d')

        self.assertTrue(p0.equals(p1))
        self.assertTrue(p0.equals(p2))
        self.assertTrue(p0.equals(p3))
        self.assertTrue(p1.equals(p2))
        self.assertTrue(p1.equals(p3))
        self.assertTrue(p2.equals(p3))
        self.assertFalse(p2.equals(p4))

    def test_equals_nary_mary(self):
        m0, m1 = tree('ab,2ab')

        self.assertFalse(m0.equals(m1))

    def test_equals_div(self):
        d0, d1, d2 = tree('a / b,a / b,b / a')

        self.assertTrue(d0.equals(d1))
        self.assertFalse(d0.equals(d2))

    def test_equals_neg(self):
        a0, a1 = tree('-a,a')
        self.assertFalse(a0.equals(a1))

        a0, a1 = tree('-a,-a')
        self.assertTrue(a0.equals(a1))

        m0, m1 = tree('-5 * -3,-5 * 6')
        self.assertFalse(m0.equals(m1))

    def test_scope___init__(self):
        self.assertEqual(self.scope.node, self.n)
        self.assertEqual(self.scope.nodes, [self.a, self.b, self.cd])

    def test_scope_remove_leaf(self):
        self.scope.remove(self.b)
        self.assertEqual(self.scope.nodes, [self.a, self.cd])

    def test_scope_remove_node(self):
        self.scope.remove(self.cd)
        self.assertEqual(self.scope.nodes, [self.a, self.b])

    def test_scope_remove_error(self):
        with self.assertRaises(ValueError):
            self.scope.remove(self.f)

    def test_scope_replace(self):
        self.scope.replace(self.cd, self.f)
        self.assertEqual(self.scope.nodes, [self.a, self.b, self.f])

    def test_nary_node(self):
        a, b, c, d = tree('a,b,c,d')

        self.assertEqualNodes(nary_node('+', [a]), a)
        self.assertEqualNodes(nary_node('+', [a, b]), N('+', a, b))
        self.assertEqualNodes(nary_node('+', [a, b, c]),
                              N('+', N('+', a, b), c))
        self.assertEqualNodes(nary_node('+', [a, b, c, d]),
                              N('+', N('+', N('+', a, b), c), d))

    def test_scope_as_nary_node(self):
        self.assertEqualNodes(self.scope.as_nary_node(), self.n)
