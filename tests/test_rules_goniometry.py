from src.rules.goniometry import match_add_quadrants, add_quadrants
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesGoniometry(RulesTestCase):

    def test_match_add_quadrants(self):
        root = tree('sin(x) ^ 2 + cos(x) ^ 2')
        possibilities = match_add_quadrants(root)
        self.assertEqualPos(possibilities, [P(root, add_quadrants, ())])

    def test_add_quadrants(self):
        root = tree('sin(x) ^ 2 + cos(x) ^ 2')
        self.assertEqual(add_quadrants(root, ()), 1)
