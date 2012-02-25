# vim: set fileencoding=utf-8 :
from src.rules.goniometry import match_add_quadrants, add_quadrants, \
        match_negated_parameter, negated_sinus_parameter, \
        negated_cosinus_parameter, sin, cos
from src.possibilities import Possibility as P
from tests.rulestestcase import RulesTestCase, tree


class TestRulesGoniometry(RulesTestCase):

    def test_match_add_quadrants(self):
        root = tree('sin t ^ 2 + cos t ^ 2')
        possibilities = match_add_quadrants(root)
        self.assertEqualPos(possibilities, [P(root, add_quadrants, ())])

    def test_add_quadrants(self):
        self.assertEqual(add_quadrants(None, ()), 1)

    def test_match_negated_parameter(self):
        s, c = tree('sin -t, cos -t')
        t = s[0]

        self.assertEqualPos(match_negated_parameter(s), \
                [P(s, negated_sinus_parameter, (t,))])

        self.assertEqualPos(match_negated_parameter(c), \
                [P(c, negated_cosinus_parameter, (t,))])

    def test_negated_sinus_parameter(self):
        s = tree('sin -t')
        t = s[0]
        self.assertEqual(negated_sinus_parameter(s, (t,)), -sin(+t))

    def test_negated_cosinus_parameter(self):
        c = tree('cos -t')
        t = c[0]
        self.assertEqual(negated_cosinus_parameter(c, (t,)), cos(+t))
