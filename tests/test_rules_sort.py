from src.rules.sort import match_sort_multiplicants, move_constant
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesSort(RulesTestCase):

    def test_match_sort_multiplicants(self):
        x, l2 = root = tree('x * 2')
        possibilities = match_sort_multiplicants(root)
        self.assertEqualPos(possibilities,
                [P(root, move_constant, (Scope(root), l2, x))])

    def test_move_constant(self):
        x, l2 = root = tree('x * 2')
        self.assertEqualNodes(move_constant(root, (Scope(root), l2, x)),
                              l2 * x)
