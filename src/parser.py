#!/usr/bin/env python
"""
This parser will parse the given input and build an expression tree. Grammar
file for the supported mathematical expressions.
"""

from node import ExpressionNode as Node, ExpressionLeaf as Leaf

import argparse

import os.path
PYBISON_BUILD = os.path.realpath('build/external/pybison')
PYBISON_PYREX = os.path.realpath('external/pybison/src/pyrex')

import sys
sys.path.insert(0, PYBISON_BUILD)
sys.path.insert(1, PYBISON_PYREX)

from bison import BisonParser, ParserSyntaxError


# Check for n-ary operator in child nodes
def combine(op, n):
    return n.nodes if n.title() == op else [n]

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
              'LPAREN', 'RPAREN', 'COMMA', 'CONCAT_POW',
              'NEWLINE', 'QUIT', 'RAISE']

    # ------------------------------
    # precedences
    # ------------------------------
    precedences = (
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

    # ------------------------------------------------------------------
    # override default read method with a version that prompts for input
    # ------------------------------------------------------------------
    def read(self, nbytes):
        try:
            return raw_input('>>> ') + '\n'
        except EOFError:
            return ''

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
             | RAISE NEWLINE
        """
        if option == 1:
            return values[0]

        if option == 2:
            raise RuntimeError('on_line: exception raised')

    def on_exp(self, target, option, names, values):
        """
        exp : NUMBER
            | IDENTIFIER
            | LPAREN exp RPAREN
            | unary
            | binary
            | concat
        """

        if option == 0:  # rule: NUMBER
            # TODO: A bit hacky, this achieves long integers and floats.
            value = float(values[0]) if '.' in values[0] else int(values[0])
            return Leaf(value)

        if option == 1:  # rule: IDENTIFIER
            return Leaf(values[0])

        if option == 2:  # rule: LPAREN exp RPAREN
            return values[1]

        if option in [3, 4, 5]:  # rule: unary | binary | concat
            return values[0]

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))

    def on_unary(self, target, option, names, values):
        """
        unary : MINUS exp %prec NEG
        """

        if option == 0:  # rule: NEG exp
            return Node('-', values[1])

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))

    def on_binary(self, target, option, names, values):
        """
        binary : exp PLUS exp
               | exp MINUS exp
               | exp TIMES exp
               | exp DIVIDE exp
               | exp POW exp
        """

        if option == 0:  # rule: exp PLUS exp
            return Node('+', *(combine('+', values[0])
                               + combine('+', values[2])))

        if option == 1:  # rule: exp MINUS exp
            return Node('-', *(combine('-', values[0])
                               + combine('-', values[2])))

        if option == 2:  # rule: exp TIMES exp
            return Node('*', *(combine('*', values[0])
                               + combine('*', values[2])))

        if option == 3:  # rule: exp DIVIDE exp
            return Node('/', values[0], values[2])

        if option == 4:  # rule: exp POW exp
            return Node('^', values[0], values[2])

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))


    def on_concat(self, option, target, names, values):
        """
        concat : exp IDENTIFIER
               | exp NUMBER
               | exp LPAREN exp RPAREN
               | exp CONCAT_POW
               | CONCAT_POW
        """

        if option in [0, 1]:  # rule: exp IDENTIFIER | exp NUMBER
            # NOTE: xy -> x*y
            # NOTE: (x)4 -> x*4
            val = int(values[1]) if option == 1 else values[1]
            return Node('*', *(combine('*', values[0]) + [Leaf(val)]))

        if option == 2:  # rule: exp LPAREN exp RPAREN
            # NOTE: x(y) -> x*(y)
            return Node('*', *(combine('*', values[0])
                              + combine('*', values[2])))

        if option == 3:
            # NOTE: x4 -> x^4
            identifier, exponent = list(values[1])
            node = Node('^', Leaf(identifier), Leaf(int(exponent)))
            return Node('*', values[0], node)

        if option == 4:
            # NOTE: x4 -> x^4
            identifier, exponent = list(values[0])
            return Node('^', Leaf(identifier), Leaf(int(exponent)))

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))

    # -----------------------------------------
    # raw lex script, verbatim here
    # -----------------------------------------
    lexscript = r"""
    %{
    //int yylineno = 0;
    #include "Python.h"
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
    %}

    %%

    [a-zA-Z][0-9]+ { returntoken(CONCAT_POW); }
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
    "quit"    { printf("lex: got QUIT\n"); yyterminate(); returntoken(QUIT); }
    "raise"   { returntoken(RAISE); }

    [ \t\v\f] {}
    [\n]      {yylineno++; returntoken(NEWLINE); }
    .         { printf("unknown char %c ignored, yytext=%p\n",
                yytext[0], yytext); /* ignore bad chars */}

    %%

    yywrap() { return(1); }
    """


def get_args():
    parser = argparse.ArgumentParser(prog='parser', description=__doc__)
    parser.add_argument('--debug', '-d', action='store_true', default=False,
            help='Enable debug mode in bison and flex.')
    parser.add_argument('--verbose', '-v', action='store_true', default=False,
            help='Enable verbose output messages (printed to stdout).')
    parser.add_argument('--keepfiles', '-k', action='store_true', default=False,
            help='Keep temporary generated bison and lex files.')
    parser.add_argument('--batch', '-b', action='store_true', default=False,
            help='Disable interactive mode and execute expressions in batch mode.')
    return parser.parse_args()


def main():
    args = get_args()

    p = Parser(verbose=args.verbose,
               keepfiles=args.keepfiles,
               interactive=not args.batch)

    node = p.run(debug=args.debug)

    # Clear the line, when the shell exits.
    if not args.batch:
        print

    return node


if __name__ == '__main__':
    main()