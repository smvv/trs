from src.rules.factors import match_expand, expand_single, expand_double
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase
from tests.test_rules_poly import tree


class TestRulesFactors(RulesTestCase):

    def test_match_expand(self):
        a, bc, d = tree('a,b + c,d')
        b, c = bc

        root = a * bc
        possibilities = match_expand(root)
        self.assertEqualPos(possibilities,
                [P(root, expand_single, (a, bc))])

        root = bc * a
        possibilities = match_expand(root)
        self.assertEqualPos(possibilities,
                [P(root, expand_single, (a, bc))])

        root = a * d * bc
        possibilities = match_expand(root)
        self.assertEqualPos(possibilities,
                [P(root, expand_single, (a, bc)),
                 P(root, expand_single, (d, bc))])

        ab, cd = root = (a + b) * (c + d)
        possibilities = match_expand(root)
        self.assertEqualPos(possibilities,
                [P(root, expand_double, (ab, cd))])

    def test_expand_single(self):
        a, b, c, d = tree('a,b,c,d')
        bc = b + c

        root = a * bc
        self.assertEqualNodes(expand_single(root, (a, bc)),
                              a * b + a * c)

        root = a * d * bc
        self.assertEqualNodes(expand_single(root, (a, bc)),
                              (a * b + a * c) * d)

    def test_expand_double(self):
        (a, b), (c, d) = ab, cd = tree('a + b,c + d')

        root = ab * cd
        self.assertEqualNodes(expand_double(root, (ab, cd)),
                              a * c + a * d + b * c + b * d)

        root = a * ab * b * cd * c
        self.assertEqualNodes(expand_double(root, (ab, cd)),
                              a * (a * c + a * d + b * c + b * d) * b * c)
