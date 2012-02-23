from tests.rulestestcase import RulesTestCase as TestCase, rewrite


class TestLeidenOefenopgave(TestCase):
    def test_1_1(self):
        for chain in [['-5(x2 - 3x + 6)', '-5(x ^ 2 - 3x) - 5 * 6',
                       '-5x ^ 2 - 5 * -3x - 5 * 6',
                       '-5x ^ 2 - -15x - 5 * 6',
                       '-5x ^ 2 + 15x - 5 * 6',
                       '-5x ^ 2 + 15x - 30',
                       ],
                     ]:
            self.assertRewrite(chain)

        return

        for exp, solution in [
                ('-5(x2 - 3x + 6)',       '-30 + 15x - 5x ^ 2'),
                ('(x+1)^2',              'x ^ 2 + 2x + 1'),
                ('(x-1)^2',              'x ^ 2 - 2x + 1'),
                ('(2x+x)*x',             '3x ^ 2'),
                ('-2(6x-4)^2*x',         '-72x ^ 3 + 96x ^ 2 + 32x'),
                ('(4x + 5) * -(5 - 4x)', '16x^2 - 25'),
                ]:
            self.assertEqual(str(rewrite(exp)), solution)

    def test_1_2(self):
        for chain in [['(x+1)^3', '(x + 1)(x + 1) ^ 2',
                '(x + 1)(x + 1)(x + 1)',
                '(xx + x * 1 + 1x + 1 * 1)(x + 1)',
                '(x ^ (1 + 1) + x * 1 + 1x + 1 * 1)(x + 1)',
                '(x ^ 2 + x * 1 + 1x + 1 * 1)(x + 1)',
                '(x ^ 2 + x + 1x + 1 * 1)(x + 1)',
                '(x ^ 2 + x + x + 1 * 1)(x + 1)',
                '(x ^ 2 + (1 + 1)x + 1 * 1)(x + 1)',
                '(x ^ 2 + 2x + 1 * 1)(x + 1)',
                '(x ^ 2 + 2x + 1)(x + 1)',
                '(x ^ 2 + 2x)x + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'xx ^ 2 + x * 2x + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ (1 + 2) + x * 2x + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ 3 + x * 2x + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ 3 + 2xx + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ 3 + 2x ^ (1 + 1) + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ 3 + 2x ^ 2 + (x ^ 2 + 2x) * 1 + 1x + 1 * 1',
                'x ^ 3 + 2x ^ 2 + 1x ^ 2 + 1 * 2x + 1x + 1 * 1',
                'x ^ 3 + 2x ^ 2 + x ^ 2 + 1 * 2x + 1x + 1 * 1',
                'x ^ 3 + (2 + 1)x ^ 2 + 1 * 2x + 1x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + 1 * 2x + 1x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + 2x + 1x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + 2x + x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + (2 + 1)x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + 3x + 1 * 1',
                'x ^ 3 + 3x ^ 2 + 3x + 1',
                ]
            ]:
            self.assertRewrite(chain)

    def test_1_3(self):
        # (x+1)^2 -> x^2 + 2x + 1
        for chain in [['(x+1)^2', '(x + 1)(x + 1)',
                       'xx + x * 1 + 1x + 1 * 1',
                       'x ^ (1 + 1) + x * 1 + 1x + 1 * 1',
                       'x ^ 2 + x * 1 + 1x + 1 * 1',
                       'x ^ 2 + x + 1x + 1 * 1',
                       'x ^ 2 + x + x + 1 * 1',
                       'x ^ 2 + (1 + 1)x + 1 * 1',
                       'x ^ 2 + 2x + 1 * 1',
                       'x ^ 2 + 2x + 1'],
                     ]:
            self.assertRewrite(chain)

    def test_1_4(self):
        # (x-1)^2 -> x^2 - 2x + 1
        for chain in [['(x-1)^2', '(x - 1)(x - 1)',
                       'xx + x * -1 - 1x - 1 * -1',
                       'x ^ (1 + 1) + x * -1 - 1x - 1 * -1',
                       'x ^ 2 + x * -1 - 1x - 1 * -1',
                       'x ^ 2 - x * 1 - 1x - 1 * -1',
                       'x ^ 2 - x - 1x - 1 * -1',
                       'x ^ 2 - x - x - 1 * -1',
                       'x ^ 2 + (1 + 1) * -x - 1 * -1',
                       'x ^ 2 + 2 * -x - 1 * -1',
                       'x ^ 2 - 2x - 1 * -1',
                       'x ^ 2 - 2x - -1',
                       'x ^ 2 - 2x + 1',
                     ]]:
            self.assertRewrite(chain)

    def test_1_4_1(self):
        self.assertRewrite(['x * -1 + 1x',
                            '-x * 1 + 1x',
                            '-x + 1x',
                            '-x + x',
                            '(-1 + 1)x',
                            '0x',
                            '0'])

    def test_1_4_2(self):
        self.assertRewrite(['x * -1 - 1x',
                            '-x * 1 - 1x',
                            '-x - 1x',
                            '-x - x',
                            '(1 + 1) * -x',
                            '2 * -x',
                            '-2x'])

    def test_1_4_3(self):
        self.assertRewrite(['x * -1 + x * -1',
                            '-x * 1 + x * -1',
                            '-x + x * -1',
                            '-x - x * 1',
                            '-x - x',
                            '(1 + 1) * -x',
                            '2 * -x',
                            '-2x'])

    def test_1_5(self):
        self.assertRewrite(['(2x + x)x', '(2 + 1)xx', '3xx',
                            '3x ^ (1 + 1)', '3x ^ 2'])

    def test_1_7(self):
        self.assertRewrite(['(4x + 5) * -(5 - 4x)',
                            '(4x + 5)(-5 - -4x)',
                            '(4x + 5)(-5 + 4x)',
                            '4x * -5 + 4x * 4x + 5 * -5 + 5 * 4x',
                            '-20x + 4x * 4x + 5 * -5 + 5 * 4x',
                            '-20x + 16xx + 5 * -5 + 5 * 4x',
                            '-20x + 16x ^ (1 + 1) + 5 * -5 + 5 * 4x',
                            '-20x + 16x ^ 2 + 5 * -5 + 5 * 4x',
                            '-20x + 16x ^ 2 - 25 + 5 * 4x',
                            '-20x + 16x ^ 2 - 25 + 20x',
                            '(-20 + 20)x + 16x ^ 2 - 25',
                            '0x + 16x ^ 2 - 25',
                            '0 + 16x ^ 2 - 25',
                            '-25 + 16x ^ 2'])
                            # FIXME: '16 * x ^ 2 - 25'])

    def test_2(self):
        pass

    def test_3(self):
        pass

    def test_4_1(self):
        self.assertRewrite(['2/15 + 1/4', '8 / 60 + 15 / 60', '(8 + 15) / 60',
                            '23 / 60'])

    def test_4_2(self):
        self.assertRewrite(['2/7 - 4/11', '22 / 77 - 28 / 77',
                            '(22 - 28) / 77', '-6 / 77'])

    #def test_4_3(self):
    #    self.assertRewrite(['(7/3) * (3/5)', '7 / 5'])

    #def test_4_4(self):
    #    self.assertRewrite(['(3/4) / (5/6)', '9 / 10'])

    #def test_4_5(self):
    #    self.assertRewrite(['1/4 * 1/x', '1 / (4x)'])

    #def test_4_6(self):
    #    self.assertRewrite(['(3/x^2) / (x/7)', '21 / x^3'])

    #def test_4_7(self):
    #    self.assertRewrite(['1/x + 2/(x+1)', '(3x + 1) / (x * (x + 1))'])
