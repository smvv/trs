from src.rules.logarithmic import log, ln, match_constant_logarithm, \
        base_equals_raised, logarithm_of_one, divide_same_base, \
        match_add_logarithms, add_logarithms, expand_negations, \
        subtract_logarithms, match_raised_base, raised_base, \
        match_factor_out_exponent, split_negative_exponent, \
        factor_out_exponent, match_factor_in_multiplicant, \
        factor_in_multiplicant
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
                [P(root, base_equals_raised),
                 P(root, divide_same_base)])

        root = tree('log(a, a)')
        self.assertEqualPos(match_constant_logarithm(root),
                [P(root, base_equals_raised),
                 P(root, divide_same_base)])

    def test_logarithm_of_one(self):
        root = tree('log 1')
        self.assertEqual(logarithm_of_one(root, ()), 0)

    def test_divide_same_base(self):
        root, l5, l6 = tree('log(5, 6), 5, 6')
        self.assertEqual(divide_same_base(root, ()), log(l5) / log(l6))

    def test_match_add_logarithms(self):
        root = tree('log a + ln b')
        self.assertEqualPos(match_add_logarithms(root), [])

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
        root, expect = tree('log a + log b, log(ab)')
        log_a, log_b = root
        self.assertEqual(add_logarithms(root, (Scope(root), log_a, log_b)),
                         expect)

    def test_expand_negations(self):
        root, expect = tree('-log(a) - log(b), -(log(a) + log(b))')
        log_a, log_b = root
        self.assertEqual(expand_negations(root, (Scope(root), log_a, log_b)),
                         expect)

    def test_subtract_logarithms(self):
        root, expect = tree('log(a) - log(b), log(a / b)')
        loga, logb = root
        self.assertEqual(subtract_logarithms(root, (Scope(root), loga, logb)),
                         expect)

        root, expect = tree('-log(a) + log(b), log(b / a)')
        loga, logb = root
        self.assertEqual(subtract_logarithms(root, (Scope(root), logb, loga)),
                         expect)

    def test_match_raised_base(self):
        root, a = tree('2 ^ log_2(a), a')
        self.assertEqualPos(match_raised_base(root),
                [P(root, raised_base, (a,))])

        root, a = tree('e ^ ln(a), a')
        self.assertEqualPos(match_raised_base(root),
                [P(root, raised_base, (a,))])

        root = tree('2 ^ log_3(a)')
        self.assertEqualPos(match_raised_base(root), [])

    def test_raised_base(self):
        root, a = tree('2 ^ log_2(a), a')
        self.assertEqual(raised_base(root, (root[1][0],)), a)

    def test_match_factor_out_exponent(self):
        for root in tree('log(a ^ 2), log(2 ^ a), log(a ^ a), log(2 ^ 2)'):
            self.assertEqualPos(match_factor_out_exponent(root),
                    [P(root, factor_out_exponent)])

        root = tree('log(a ^ -b)')
        self.assertEqualPos(match_factor_out_exponent(root),
                [P(root, split_negative_exponent),
                 P(root, factor_out_exponent)])

    def test_split_negative_exponent(self):
        root, expect = tree('log(a ^ -b), log((a ^ b) ^ -1)')
        self.assertEqual(split_negative_exponent(root, ()), expect)

    def test_factor_out_exponent(self):
        ((a, l2), l10) = root = tree('log(a ^ 2)')
        self.assertEqual(factor_out_exponent(root, ()), l2 * log(a))

    def test_match_factor_in_multiplicant(self):
        root, log_3 = tree('2log(3), log(3)')
        self.assertEqualPos(match_factor_in_multiplicant(root),
                [P(root, factor_in_multiplicant, (Scope(root), 2, log_3))])

        root = tree('2log(a)')
        self.assertEqualPos(match_factor_in_multiplicant(root), [])

        root = tree('alog(3)')
        self.assertEqualPos(match_factor_in_multiplicant(root), [])

    def test_factor_in_multiplicant(self):
        root, expect = tree('2log(3), log(3 ^ 2)')
        l2, log3 = root
        self.assertEqual(factor_in_multiplicant(root, (Scope(root), l2, log3)),
                         expect)
