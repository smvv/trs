from tests.rulestestcase import RulesTestCase as TestCase


class TestRewrite(TestCase):

    def test_addition_rewrite(self):
        self.assertRewrite(['2 + 3 + 4', '5 + 4', '9'])

    def test_addition_identifiers_rewrite(self):
        self.assertRewrite(['2 + 3a + 4', '6 + 3a'])

    def test_division_rewrite(self):
        self.assertRewrite(['2/7 - 4/11', '22 / 77 - 28 / 77',
                            '(22 - 28) / 77', '-6 / 77'])
