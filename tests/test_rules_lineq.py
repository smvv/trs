from src.rules.lineq import match_move_term, swap_sides, subtract_term, \
        divide_term, multiply_term
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesLineq(RulesTestCase):

    def test_match_move_term_swap(self):
        root = tree('x = b')
        self.assertEqualPos(match_move_term(root), [])

        root = tree('a = bx')
        self.assertEqualPos(match_move_term(root), [P(root, swap_sides)])

    def test_match_move_term_subtract(self):
        root, a = tree('x + a = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, subtract_term, (a,))])

        root, cx = tree('x = b + cx, cx')
        self.assertEqualPos(match_move_term(root),
                [P(root, subtract_term, (cx,))])

    def test_match_move_term_divide(self):
        root, a = tree('ax = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, divide_term, (a,))])

    def test_match_move_term_multiply(self):
        root, a = tree('x / a = b, a')
        self.assertEqualPos(match_move_term(root),
                [P(root, multiply_term, (a,))])

        root, x = tree('a / x = b, x')
        self.assertEqualPos(match_move_term(root),
                [P(root, multiply_term, (x,))])

    def test_swap_sides(self):
        root, expect = tree('a = bx, bx = a')
        self.assertEqual(swap_sides(root, ()), expect)

    def test_subtract_term(self):
        root, a, expect = tree('x + a = b, a, x + a - a = b - a')
        self.assertEqual(subtract_term(root, (a,)), expect)

    def test_divide_term(self):
        root, a, expect = tree('x * a = b, a, x * a / a = b / a')
        self.assertEqual(divide_term(root, (a,)), expect)

    def test_multiply_term(self):
        root, a, expect = tree('x / a = b, a, x / a * a = b * a')
        self.assertEqual(multiply_term(root, (a,)), expect)

    def test_match_move_term_chain(self):
        self.assertRewrite([
            '2x + 3 = -3x - 2',
            '2x + 3 - 3 = -3x - 2 - 3',
            '2x + 0 = -3x - 2 - 3',
            '2x = -3x - 2 - 3',
            '2x = -3x - 5',
            '2x - -3x = -3x - 5 - -3x',
            '2x + 3x = -3x - 5 - -3x',
            '(2 + 3)x = -3x - 5 - -3x',
            '5x = -3x - 5 - -3x',
            '5x = -3x - 5 + 3x',
            '5x = (-3 + 3)x - 5',
            '5x = 0x - 5',
            '5x = 0 - 5',
            '5x = -5',
            '5x / 5 = -5 / 5',
            'x / 1 = -5 / 5',
            'x = -5 / 5',
            'x = -1',
        ])
