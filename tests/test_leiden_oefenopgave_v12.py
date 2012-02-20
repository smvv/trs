from tests.rulestestcase import RulesTestCase as TestCase, rewrite


class TestLeidenOefenopgaveV12(TestCase):
    def test_1_e(self):
        for chain in [['-2(6x - 4) ^ 2 * x',
                       '-2(6x - 4)(6x - 4)x',
                       '(-2 * 6x - 2 * -4)(6x - 4)x',
                       '(-12x - 2 * -4)(6x - 4)x',
                       '(-12x - -8)(6x - 4)x',
                       '(-12x + 8)(6x - 4)x',
                       '(-12x * 6x - 12x * -4 + 8 * 6x + 8 * -4)x',
                       '(-72xx - 12x * -4 + 8 * 6x + 8 * -4)x',
                       '(-72 * x ^ (1 + 1) - 12x * -4 + 8 * 6x + 8 * -4)x',
                       '(-72 * x ^ 2 - 12x * -4 + 8 * 6x + 8 * -4)x',
                       '(-72 * x ^ 2 - -48x + 8 * 6x + 8 * -4)x',
                       '(-72 * x ^ 2 - -48x + 48x + 8 * -4)x',
                       '',
                       '']
            ]:
            self.assertRewrite(chain)
