from src.rules.lineq import match_subtract_term, \
        subtract_term
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesLineq(RulesTestCase):

    def test_match_subtract_term(self):
        root, a = tree('x + a = b, a')
        self.assertEqualPos(match_subtract_term(root),
                [P(root, subtract_term, (a,))])

        root, cx = tree('x = b + cx, cx')
        self.assertEqualPos(match_subtract_term(root),
                [P(root, subtract_term, (cx,))])

    def test_subtract_term(self):
        root, a, expect = tree('x + a = b, a, x + a - a = b - a')
        self.assertEqual(subtract_term(root, (a,)), expect)
