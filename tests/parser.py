import sys

from external.graph_drawing.graph import generate_graph
from external.graph_drawing.line import generate_line
from src.node import negation_to_node


def create_graph(node):
    return generate_graph(negation_to_node(node))


class ParserWrapper(object):

    def __init__(self, base_class, **kwargs):
        self.input_buffer = []
        self.last_buffer = ''
        self.input_position = 0
        self.closed = False

        self.verbose = kwargs.get('verbose', False)

        self.parser = base_class(file=self, read=self.read, **kwargs)

    def readline(self, nbytes=False):
        return self.read(nbytes)

    def read(self, nbytes=False):

        if len(self.last_buffer) >= nbytes:
            buf = self.last_buffer[:nbytes]
            self.last_buffer = self.last_buffer[nbytes:]
            return buf

        buf = self.last_buffer

        try:
            buf += self.input_buffer[self.input_position]

            if self.verbose:
                print 'read:', buf  # pragma: nocover

            self.input_position += 1
        except IndexError:
            self.closed = True
            return ''

        self.last_buffer = buf[nbytes:]
        return buf

    def close(self):
        self.closed = True
        self.input_position = len(self.input_buffer)

    def run(self, input_buffer, *args, **kwargs):
        map(self.append, input_buffer)
        return self.parser.run(*args, **kwargs)

    def append(self, input):
        self.closed = False
        self.input_buffer.append(input + '\n')


def run_expressions(base_class, expressions, fail=True, silent=False,
        **kwargs):
    """
    Run a list of mathematical expression through the term rewriting system and
    check if the output matches the expected output. The list of EXPRESSIONS
    consists of tuples (expression, output), where expression is the
    mathematical expression to evaluate (String) and output is the expected
    output of the evaluation (thus, the output can be Float, Int or None).

    If KEEPFILES is non-zero or True, the generated Flex and Bison files will
    be kept. Otherwise, those temporary files will be deleted. If FAIL is True,
    and the output of the expression is not equal to the expected output, an
    assertion error is raised. If SILENT is False, and an assertion error is
    raised, an error message is printed on stderr. If SILENT is True, no error
    message will be printed.

    If VERBOSE is non-zero and a positive integer number, verbosity of the term
    rewriting system will be increased. This will output debug messages and a
    higher value will print more types of debug messages.
    """

    parser = ParserWrapper(base_class, **kwargs)

    for exp, out in expressions:
        res = None
        try:
            res = parser.run([exp])
            assert res == out
        except:  # pragma: nocover
            if not silent:
                print >>sys.stderr, 'error: %s gives %s, but expected: %s' \
                                    % (exp, str(res), str(out))

            if not silent and hasattr(res, 'nodes'):
                print >>sys.stderr, 'result graph:'
                print >>sys.stderr, create_graph(res)
                print >>sys.stderr, 'expected graph:'
                print >>sys.stderr, create_graph(out)

            if fail:
                raise


def apply_expressions(base_class, expressions, fail=True, silent=False,
        **kwargs):
    parser = ParserWrapper(base_class, **kwargs)

    for exp, times, out in expressions:
        res = None
        try:
            parser.run([exp])
            parser.parser.rewrite(check_implicit=False)
            res = parser.parser.root_node
            assert res == out
        except:  # pragma: nocover
            if not silent:
                print >>sys.stderr, 'error: %s gives %s, but expected: %s' \
                                    % (exp, str(res), str(out))

            if not silent and hasattr(res, 'nodes'):
                print >>sys.stderr, 'result graph:'
                print >>sys.stderr, create_graph(res)
                print >>sys.stderr, 'expected graph:'
                print >>sys.stderr, create_graph(out)

            if fail:
                raise


def graph(parser, *exp, **kwargs):
    return create_graph(ParserWrapper(parser, **kwargs).run(exp))


def line(parser, *exp, **kwargs):
    return generate_line(ParserWrapper(parser, **kwargs).run(exp))
