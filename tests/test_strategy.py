from src.rules.factors import match_expand, expand_double, expand_single
from src.node import Scope
from src.possibilities import Possibility as P
from src.strategy import find_possibilities
from tests.rulestestcase import RulesTestCase, tree


class TestStrategy(RulesTestCase):

    def test_find_possibilities_sort(self):
        (ab, cd), e = root = tree('(a + b)(c + d)e')
        self.assertEqualPos(find_possibilities(root),
                [P(root, expand_single, (Scope(root), cd, e)),
                 P(root, expand_single, (Scope(root), ab, e)),
                 P(root, expand_double, (Scope(root), ab, cd))])
