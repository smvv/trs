from src.rules.factors import match_expand, expand_double, expand_single
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesFactors(RulesTestCase):

    def test_match_expand(self):
        a, bc, d = tree('a,b + c,d')
        b, c = bc

        root = a * bc
        self.assertEqualPos(match_expand(root),
                [P(root, expand_single, (Scope(root), a, bc))])

        root = bc * a
        self.assertEqualPos(match_expand(root),
                [P(root, expand_single, (Scope(root), bc, a))])

        root = a * bc * d
        self.assertEqualPos(match_expand(root),
                [P(root, expand_single, (Scope(root), a, bc)),
                 P(root, expand_single, (Scope(root), bc, d))])

        ab, cd = root = (a + b) * (c + d)
        self.assertEqualPos(match_expand(root),
                [P(root, expand_double, (Scope(root), ab, cd))])

        (ab, cd), e = root = tree('(a + b)(c + d)e')
        self.assertEqualPos(match_expand(root),
                [P(root, expand_double, (Scope(root), ab, cd)),
                 P(root, expand_single, (Scope(root), cd, e)),
                 P(root, expand_single, (Scope(root), ab, e))])

    def test_expand_single(self):
        root, expect = tree('a(b + c), ab + ac')
        a, bc = root
        self.assertEqualNodes(expand_single(root, (Scope(root), a, bc)),
                              expect)

        root, expect = tree('a(b+c)d, a(bd + cd)')
        (a, bc), d = root
        self.assertEqualNodes(expand_single(root, (Scope(root), bc, d)),
                              expect)

    def test_expand_double(self):
        (a, b), (c, d) = ab, cd = tree('a + b,c + d')

        root, expect = tree('(a + b)(c + d), ac + ad + bc + bd')
        ab, cd = root
        self.assertEqualNodes(expand_double(root, (Scope(root), ab, cd)),
                              expect)

        root, expect = tree('a(a + b)b(c + d)c, a(ac + ad + bc + bd)bc')
        (((a, ab), b), cd), c = root
        self.assertEqualNodes(expand_double(root, (Scope(root), ab, cd)),
                              expect)
