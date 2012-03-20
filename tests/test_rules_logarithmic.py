from src.rules.logarithmic import log, ln, match_constant_logarithm, \
        logarithm_of_one, divide_same_base, match_add_logarithms, \
        add_logarithms, expand_negations, subtract_logarithms
from src.node import Scope
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesLogarithmic(RulesTestCase):

    def test_match_constant_logarithm(self):
        self.assertRaises(ValueError, tree, 'log_1(a)')

        root = tree('log 1')
        self.assertEqualPos(match_constant_logarithm(root),
                [P(root, logarithm_of_one)])

        root = tree('log 10')
        self.assertEqualPos(match_constant_logarithm(root),
                [P(root, divide_same_base)])

        root = tree('log(a, a)')
        self.assertEqualPos(match_constant_logarithm(root),
                [P(root, divide_same_base)])

    def test_match_add_logarithms(self):
        log_a, log_b = root = tree('log a + log b')
        self.assertEqualPos(match_add_logarithms(root),
                [P(root, add_logarithms, (Scope(root), log_a, log_b))])

        log_a, log_b = root = tree('-log a - log b')
        self.assertEqualPos(match_add_logarithms(root),
                [P(root, expand_negations, (Scope(root), log_a, log_b))])

        log_a, log_b = root = tree('log a - log b')
        self.assertEqualPos(match_add_logarithms(root),
                [P(root, subtract_logarithms, (Scope(root), log_a, log_b))])

        log_a, log_b = root = tree('-log a + log b')
        self.assertEqualPos(match_add_logarithms(root),
                [P(root, subtract_logarithms, (Scope(root), log_b, log_a))])

    def test_add_logarithms(self):
        root, a, b = tree('log a + log b, a, b')
        log_a, log_b = root
        self.assertEqual(add_logarithms(root, (Scope(root), log_a, log_b)),
                         log(a * b))
