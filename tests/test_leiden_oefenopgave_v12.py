from tests.rulestestcase import RulesTestCase as TestCase


class TestLeidenOefenopgaveV12(TestCase):
    def test_1_a(self):
        self.assertRewrite(['-5(x2 - 3x + 6)',
                            '-5(x ^ 2 - 3x) - 5 * 6',
                            '-5x ^ 2 - 5 * -3x - 5 * 6',
                            '-5x ^ 2 - -15x - 5 * 6',
                            '-5x ^ 2 + 15x - 5 * 6',
                            '-5x ^ 2 + 15x - 30'])

    def test_1_d(self):
        self.assertRewrite(['(2x + x)x',
                            '(2 + 1)xx',
                            '3xx',
                            '3x ^ (1 + 1)',
                            '3x ^ 2'])

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
            '-x ^ (1 + 2) * 72 + x * 96x + x * -32',
            '-x ^ 3 * 72 + x * 96x + x * -32',
            '-x ^ 3 * 72 + x ^ (1 + 1) * 96 + x * -32',
            '-x ^ 3 * 72 + x ^ 2 * 96 + x * -32',
            '-x ^ 3 * 72 + x ^ 2 * 96 - x * 32',
            '72 * -x ^ 3 + x ^ 2 * 96 - x * 32',
            '-72x ^ 3 + x ^ 2 * 96 - x * 32',
            '-72x ^ 3 + 96x ^ 2 - x * 32',
            '-72x ^ 3 + 96x ^ 2 + 32 * -x',
            '-72x ^ 3 + 96x ^ 2 - 32x',
        ])

    def test_2_a(self):
        self.assertRewrite([
            '(a2b^-1)^3(ab2)',
            '(a ^ 2 * (1 / b ^ 1)) ^ 3 * ab ^ 2',
            '(a ^ 2 * (1 / b)) ^ 3 * ab ^ 2',
            '(a ^ 2 * 1 / b) ^ 3 * ab ^ 2',
            '(a ^ 2 / b) ^ 3 * ab ^ 2',
            '(a ^ 2) ^ 3 / b ^ 3 * ab ^ 2',
            'a ^ (2 * 3) / b ^ 3 * ab ^ 2',
            'a ^ 6 / b ^ 3 * ab ^ 2',
            'aa ^ 6 / b ^ 3 * b ^ 2',
            'a ^ (1 + 6) / b ^ 3 * b ^ 2',
            'a ^ 7 / b ^ 3 * b ^ 2',
            'b ^ 2 * a ^ 7 / b ^ 3',
            'b ^ 2 / b ^ 3 * a ^ 7 / 1',
            'b ^ (2 - 3)a ^ 7 / 1',
            'b ^ -1 * a ^ 7 / 1',
            '1 / b ^ 1 * a ^ 7 / 1',
            '1 / b * a ^ 7 / 1',
            'a ^ 7 * 1 / b / 1',
            'a ^ 7 / b / 1',
            'a ^ 7 / b',
        ])

    def test_2_b(self):
        self.assertRewrite([
            'a3b2a3',
            'a ^ (3 + 3)b ^ 2',
            'a ^ 6 * b ^ 2',
        ])

    def test_2_c(self):
        self.assertRewrite([
            'a5+a3',
            'a ^ 5 + a ^ 3',
        ])

    def test_2_d(self):
        self.assertRewrite([
            'a2+a2',
            '(1 + 1)a ^ 2',
            '2a ^ 2',
        ])

    def test_2_e(self):
        self.assertRewrite([
            '4b^-2',
            '4(1 / b ^ 2)',
            '4 * 1 / b ^ 2',
        ])

    def test_2_f(self):
        self.assertRewrite([
            '(4b) ^ -2',
            '4 ^ -2 * b ^ -2',
            '1 / 4 ^ 2 * b ^ -2',
            '1 / 16 * b ^ -2',
            '1 / 16 * (1 / b ^ 2)',
            '1 * 1 / (16b ^ 2)',
            '1 / (16b ^ 2)',
        ])
