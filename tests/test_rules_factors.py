from src.rules.factors import match_expand, expand_single, expand_double
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
                [P(root, expand_single, (Scope(root), a, bc))])

        root = a * d * bc
        self.assertEqualPos(match_expand(root),
                [P(root, expand_single, (Scope(root), a, bc)),
                 P(root, expand_single, (Scope(root), d, bc))])

        ab, cd = root = (a + b) * (c + d)
        self.assertEqualPos(match_expand(root),
                [P(root, expand_double, (Scope(root), ab, cd))])

    def test_expand_single(self):
        a, b, c, d = tree('a,b,c,d')
        bc = b + c

        root = a * bc
        self.assertEqualNodes(expand_single(root, (Scope(root), a, bc)),
                              a * b + a * c)

        root = a * d * bc
        self.assertEqualNodes(expand_single(root, (Scope(root), a, bc)),
                              (a * b + a * c) * d)

    def test_expand_double(self):
        (a, b), (c, d) = ab, cd = tree('a + b,c + d')

        root = ab * cd
        self.assertEqualNodes(expand_double(root, (Scope(root), ab, cd)),
                              a * c + a * d + b * c + b * d)

        root = a * ab * b * cd * c
        self.assertEqualNodes(expand_double(root, (Scope(root), ab, cd)),
                              a * (a * c + a * d + b * c + b * d) * b * c)
