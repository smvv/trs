from src.rules.sort import match_sort_polynome, swap_factors, \
        match_sort_molinome, iter_pairs
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesSort(RulesTestCase):

    def test_match_sort_molinome_constant(self):
        x, l2 = root = tree('x * 2')
        self.assertEqualPos(match_sort_molinome(root),
                [P(root, swap_factors, (Scope(root), x, l2))])

        root = tree('2x')
        self.assertEqualPos(match_sort_molinome(root), [])

    #def test_match_sort_molinome_variables(self):
    #    y, x = root = tree('yx')
    #    self.assertEqualPos(match_sort_molinome(root),
    #            [P(root, swap_factors, (Scope(root), y, x))])

    #    root = tree('xy')
    #    self.assertEqualPos(match_sort_molinome(root), [])

    def test_swap_factors(self):
        x, l2 = root = tree('x * 2')
        self.assertEqualNodes(swap_factors(root, (Scope(root), x, l2)),
                              l2 * x)
