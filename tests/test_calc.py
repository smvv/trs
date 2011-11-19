import unittest


from src.calc import Parser


class TestParser(Parser):

    def __init__(self, input_buffer, **kwargs):
        Parser.__init__(self, **kwargs)

        self.input_buffer = []
        self.input_position = 0

        map(self.append, input_buffer)

    def append(self, input):
        self.input_buffer.append(input + '\n')

    def read(self, nbytes):
        buffer = ''

        try:
            buffer = self.input_buffer[self.input_position]
        except IndexError:
            return ''

        self.input_position += 1

        return buffer


class TestCalc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        assert TestParser(['1+4'], keepfiles=1).run() == 5.0
