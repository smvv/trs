from tests.rulestestcase import RulesTestCase as TestCase, rewrite


class TestLeidenOefenopgaveV12(TestCase):
    def test_1_e(self):
        self.assertRewrite([
            '-2(6x - 4) ^ 2x',
            '-2(6x - 4)(6x - 4)x',
            '(-2 * 6x - 2 * -4)(6x - 4)x',
            '(-12x - 2 * -4)(6x - 4)x',
            '(-12x - -8)(6x - 4)x',
            '(-12x + 8)(6x - 4)x',
            '(-12x * 6x - 12x * -4 + 8 * 6x + 8 * -4)x',
            '(-72xx - 12x * -4 + 8 * 6x + 8 * -4)x',
            '(-72x ^ (1 + 1) - 12x * -4 + 8 * 6x + 8 * -4)x',
            '(-72x ^ 2 - 12x * -4 + 8 * 6x + 8 * -4)x',
            '(-72x ^ 2 - -48x + 8 * 6x + 8 * -4)x',
            '(-72x ^ 2 + 48x + 8 * 6x + 8 * -4)x',
            '(-72x ^ 2 + 48x + 48x + 8 * -4)x',
            '(-72x ^ 2 + (1 + 1) * 48x + 8 * -4)x',
            '(-72x ^ 2 + 2 * 48x + 8 * -4)x',
            '(-72x ^ 2 + 96x + 8 * -4)x',
            '(-72x ^ 2 + 96x - 32)x',
            'x(-72x ^ 2 + 96x) + x * -32',
            'x * -72x ^ 2 + x * 96x + x * -32',
            '-x * 72x ^ 2 + x * 96x + x * -32',
            '72 * -xx ^ 2 + x * 96x + x * -32',
            '-72xx ^ 2 + x * 96x + x * -32',
            '-72x ^ (1 + 2) + x * 96x + x * -32',
            '-72x ^ 3 + x * 96x + x * -32',
            '-72x ^ 3 + 96xx + x * -32',
            '-72x ^ 3 + 96x ^ (1 + 1) + x * -32',
            '-72x ^ 3 + 96x ^ 2 + x * -32',
            '-72x ^ 3 + 96x ^ 2 - x * 32',
            '-72x ^ 3 + 96x ^ 2 + 32 * -x',
            '-72x ^ 3 + 96x ^ 2 - 32x'])
            # TODO: Should powers have a higher precedence than negation
            #       while printing?
