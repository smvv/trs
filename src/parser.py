#!/usr/bin/env python
"""
This parser will parse the given input and build an expression tree. Grammar
file for the supported mathematical expressions.
"""

from node import ExpressionNode as Node, ExpressionLeaf as Leaf

import argparse

import os.path
PYBISON_BUILD = os.path.realpath('build/external/pybison')
EXTERNAL_MODS = os.path.realpath('external')

import sys
sys.path.insert(0, PYBISON_BUILD)
sys.path.insert(1, EXTERNAL_MODS)

from pybison import BisonParser, BisonSyntaxError
from graph_drawing.graph import generate_graph

from node import TYPE_OPERATOR, OP_COMMA
from rules import RULES
from possibilities import filter_duplicates


# Check for n-ary operator in child nodes
def combine(op, op_type, *nodes):
    # At least return the operator.
    res = [op]

    for n in nodes:
        # Merge the children for all nodes which have the same operator.
        if n.type == TYPE_OPERATOR and n.op == op_type:
            res += n.nodes
        else:
            res.append(n)

    return res


class Parser(BisonParser):
    """
    Implements the calculator parser. Grammar rules are defined in the method
    docstrings. Scanner rules are in the 'lexscript' attribute.
    """

    # Output directory of generated pybison files, including a trailing slash.
    buildDirectory = PYBISON_BUILD + '/'

    # ----------------------------------------------------------------
    # lexer tokens - these must match those in your lex script (below)
    # ----------------------------------------------------------------
    # TODO: add a runtime check to verify that this token list match the list
    # of tokens of the lex script.
    tokens = ['NUMBER', 'IDENTIFIER',
              'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW',
              'LPAREN', 'RPAREN', 'COMMA',
              'NEWLINE', 'QUIT', 'RAISE', 'GRAPH']

    # ------------------------------
    # precedences
    # ------------------------------
    precedences = (
        ('left', ('COMMA', )),
        ('left', ('MINUS', 'PLUS')),
        ('left', ('TIMES', 'DIVIDE')),
        ('left', ('NEG', )),
        ('right', ('POW', )),
        )

    interactive = 0

    def __init__(self, **kwargs):
        BisonParser.__init__(self, **kwargs)
        self.interactive = kwargs.get('interactive', 0)
        self.timeout = kwargs.get('timeout', 0)
        self.possibilities = []

    # ------------------------------------------------------------------
    # override default read method with a version that prompts for input
    # ------------------------------------------------------------------
    def read(self, nbytes):
        if self.file == sys.stdin and self.file.closed:
            return ''

        try:
            return raw_input('>>> ' if self.interactive else '') + '\n'
        except EOFError:
            return ''

    def hook_read_before(self):
        if self.interactive and self.possibilities:
            print 'possibilities:'
            items = filter_duplicates(self.possibilities)
            print '  ' + '\n  '.join(map(str, items))

        self.possibilities = []

    def hook_read_after(self, data):
        """
        This hook will be called when the read() method returned. The data
        argument points to the data read by the read() method. This hook
        function should return the data to be used by the parser.
        """
        import re

        # TODO: remove this quick preprocessing hack. This hack enables
        # concatenated expressions, since the grammar currently does not
        # support those. This workaround will replace:
        #   - ")(" with ")*(".
        #   - "a(" with "a*(".
        #   - ")a" with ")*a".
        #   - "ab" with "a*b".
        #   - "4a" with "4*a".
        #   - "a4" with "a^4".

        pattern = ('(?:(\))\s*(\()'       # match: )(  result: ) * (
                + '|([a-z0-9])\s*(\()'    # match: a(  result: a * (
                + '|(\))\s*([a-z0-9])'    # match: )a  result: ) * a
                + '|([a-z])\s*([a-z]+)'   # match: ab  result: a * b
                + '|([0-9])\s*([a-z])'    # match: 4a  result: 4 * a
                + '|([a-z])\s*([0-9])'    # match: a4  result: a ^ 4
                + '|([0-9])\s+([0-9]))')  # match: 4 4 result: 4 * 4

        def preprocess_data(match):
            left, right = filter(None, match.groups())

            # Filter words (otherwise they will be preprocessed as well)
            if left + right in ['graph', 'raise']:
                return left + right

            # If all characters on the right are numbers. e.g. "a4", the
            # expression implies exponentiation. Make sure ")4" is not
            # converted into an exponentiation, because that's multiplication.
            if left != ')' and not 48 <= ord(left) < 58 \
                    and all(map(lambda x: 48 <= ord(x) < 58, list(right))):
                return '%s^%s' % (left, right)

            # match: ab | abc | abcd (where left = "a")
            return '*'.join([left] + list(right))

        # Iteratively replace all matches.
        while True:
            data_after = re.sub(pattern, preprocess_data, data)

            if data == data_after:
                break

            if self.verbose:
                print 'hook_read_after() modified the input data:'
                print 'before:', data.replace('\n', '\\n')
                print 'after :', data_after.replace('\n', '\\n')

            data = data_after

        return data

    def hook_handler(self, target, option, names, values, retval):
        if target in ['exp', 'line', 'input'] or not retval \
                or retval.type != TYPE_OPERATOR or retval.op not in RULES:
            return retval

        for handler in RULES[retval.op]:
            self.possibilities.extend(handler(retval))

        return retval

    #def hook_run(self, filename, retval):
    #    return retval

    # ---------------------------------------------------------------
    # These methods are the python handlers for the bison targets.
    # (which get called by the bison code each time the corresponding
    # parse target is unambiguously reached)
    #
    # WARNING - don't touch the method docstrings unless you know what
    # you are doing - they are in bison rule syntax, and are passed
    # verbatim to bison to build the parser engine library.
    # ---------------------------------------------------------------

    # Declare the start target here (by name)
    start = 'input'

    def on_input(self, target, option, names, values):
        """
        input :
              | input line
        """

        if option == 1:
            # Interactive mode is enabled if the term rewriting system is used
            # as a shell. In that case, it is useful that the shell prints the
            # output of the evaluation.
            if self.interactive and values[1]:
                print values[1]

            return values[1]

    def on_line(self, target, option, names, values):
        """
        line : NEWLINE
             | exp NEWLINE
             | debug NEWLINE
             | RAISE NEWLINE
        """
        if option in [1, 2]:
            return values[0]

        if option == 3:
            raise RuntimeError('on_line: exception raised')

    def on_debug(self, target, option, names, values):
        """
        debug : GRAPH exp
        """

        if option == 0:
            print generate_graph(values[1])
            return values[1]

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_exp(self, target, option, names, values):
        """
        exp : NUMBER
            | IDENTIFIER
            | LPAREN exp RPAREN
            | unary
            | binary
            | nary
        """
        #    | concat

        if option == 0:  # rule: NUMBER
            # TODO: A bit hacky, this achieves long integers and floats.
            value = float(values[0]) if '.' in values[0] else int(values[0])
            return Leaf(value)

        if option == 1:  # rule: IDENTIFIER
            return Leaf(values[0])

        if option == 2:  # rule: LPAREN exp RPAREN
            return values[1]

        if option in [3, 4, 5]:  # rule: unary | binary | nary
            return values[0]

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_unary(self, target, option, names, values):
        """
        unary : MINUS exp %prec NEG
        """

        if option == 0:  # rule: NEG exp
            return Node('-', values[1])

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_binary(self, target, option, names, values):
        """
        binary : exp PLUS exp
               | exp MINUS exp
               | exp TIMES exp
               | exp DIVIDE exp
               | exp POW exp
        """

        if 0 <= option < 5:  # rule: exp PLUS exp
            return Node(values[1], values[0], values[2])

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_nary(self, target, option, names, values):
        """
        nary : exp COMMA exp
        """

        if option == 0:  # rule: exp COMMA exp
            return Node(*combine(',', OP_COMMA, values[0], values[2]))

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    # -----------------------------------------
    # raw lex script, verbatim here
    # -----------------------------------------
    lexscript = r"""
    %top{
    #include "Python.h"
    }

    %{
    #define YYSTYPE void *
    #include "tokens.h"
    extern void *py_parser;
    extern void (*py_input)(PyObject *parser, char *buf, int *result,
                            int max_size);
    #define returntoken(tok) \
            yylval = PyString_FromString(strdup(yytext)); return (tok);
    #define YY_INPUT(buf,result,max_size) { \
            (*py_input)(py_parser, buf, &result, max_size); \
    }

    int yycolumn = 0;

    #define YY_USER_ACTION \
            yylloc.first_line = yylloc.last_line = yylineno; \
            yylloc.first_column = yycolumn; \
            yylloc.last_column = yycolumn + yyleng; \
            yycolumn += yyleng;

    /*[a-zA-Z][0-9]+ { returntoken(CONCAT_POW); }*/
    %}

    %option yylineno

    %%

    [0-9]+    { returntoken(NUMBER); }
    [a-zA-Z]  { returntoken(IDENTIFIER); }
    "("       { returntoken(LPAREN); }
    ")"       { returntoken(RPAREN); }
    "+"       { returntoken(PLUS); }
    "-"       { returntoken(MINUS); }
    "*"       { returntoken(TIMES); }
    "^"       { returntoken(POW); }
    "/"       { returntoken(DIVIDE); }
    ","       { returntoken(COMMA); }
    "quit"    { yyterminate(); returntoken(QUIT); }
    "raise"   { returntoken(RAISE); }
    "graph"   { returntoken(GRAPH); }

    [ \t\v\f] { }
    [\n]      { yycolumn = 0; returntoken(NEWLINE); }
    .         { printf("unknown char %c ignored.\n", yytext[0]); }

    %%

    yywrap() { return(1); }
    """


def get_args():
    parser = argparse.ArgumentParser(prog='parser', description=__doc__)

    parser.add_argument('--debug', '-d', action='store_true',
            default=False,
            help='Enable debug mode in bison and flex.')
    parser.add_argument('--verbose', '-v', action='store_true',
            default=False,
            help='Enable verbose output messages (printed to stdout).')
    parser.add_argument('--keepfiles', '-k', action='store_true',
            default=False,
            help='Keep temporary generated bison and lex files.')
    parser.add_argument('--batch', '-b', action='store_true', default=False,
            help='Disable interactive mode and execute expressions in batch' \
                 ' mode.')

    return parser.parse_args()


def main():
    args = get_args()
    interactive = not args.batch and sys.stdin.isatty()

    p = Parser(verbose=args.verbose,
               keepfiles=args.keepfiles,
               interactive=interactive)

    node = p.run(debug=args.debug)

    # Clear the line, when the shell exits.
    if interactive:
        print

    return node
