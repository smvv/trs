import sys


class ParserWrapper(object):

    def __init__(self, base_class, **kwargs):
        self.input_buffer = []
        self.input_position = 0

        self.verbose = kwargs.get('verbose', False)

        # Overwrite parser read() method
        def read(nbytes):
            buf = ''

            try:
                buf = self.input_buffer[self.input_position]

                if self.verbose:
                    print 'read:', buf
            except IndexError:
                return ''

            self.input_position += 1

            return buf

        self.parser = base_class(**kwargs)
        self.parser.read = read


    def run(self, input_buffer, *args, **kwargs):
        map(self.append, input_buffer)
        return self.parser.run(*args, **kwargs)

    def append(self, input):
        self.input_buffer.append(input + '\n')


def run_expressions(base_class, expressions, keepfiles=1, fail=True,
        silent=False, verbose=0):
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

    parser = ParserWrapper(base_class, keepfiles=keepfiles, verbose=verbose)

    for exp, out in expressions:
        res = None
        try:
            res = parser.run([exp])
            assert res == out
        except:
            if not silent:
                print >>sys.stderr, 'error: %s = %s, but expected: %s' \
                                    % (exp, str(res), str(out))

            if fail:
                raise
