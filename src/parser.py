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
                print 'result:', values[1]

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
            | exp PLUS exp
            | exp MINUS exp
            | exp TIMES exp
            | exp DIVIDE exp
            | MINUS exp %prec NEG
            | exp POW exp
            | LPAREN exp RPAREN
            | symbolic
        """

        # rule: NUMBER
        if option == 0:
            # TODO: A bit hacky, this achieves long integers and floats.
            value = float(values[0]) if '.' in values[0] else int(values[0])
            return Leaf(value)

        # rule: IDENTIFIER
        if option == 1:
            return Leaf(values[0])

        # rule: LPAREN exp RPAREN
        if option == 8:
            return values[1]

        # rule: symbolic
        if option == 9:
            return values[0]

        # Check for n-ary operator in child nodes
        combine = lambda op, n: n.nodes if n.title() == op else [n]

        # rule: exp PLUS exp
        if option == 2:
            return Node('+', *(combine('+', values[0]) + combine('+', values[2])))

        # rule: exp MINUS expo
        if option == 3:
            return Node('-', *(combine('-', values[0]) + combine('-', values[2])))

        # rule: exp TIMES expo
        if option == 4:
            return Node('*', *(combine('*', values[0]) + combine('*', values[2])))

        # rule: exp DIVIDE expo
        if option == 5:
            return Node('/', values[0], values[2])

        # rule: NEG expo
        if option == 6:
            return Node('-', values[1])

        # rule: exp POW expo
        if option == 7:
            return Node('^', values[0], values[2])

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))

    def on_symbolic(self, target, option, names, values):
        """
        symbolic : NUMBER IDENTIFIER
                 | IDENTIFIER IDENTIFIER
                 | symbolic IDENTIFIER
                 | IDENTIFIER NUMBER
        """
        # rule: NUMBER IDENTIFIER
        # rule: IDENTIFIER IDENTIFIER
        # rule: symbolic IDENTIFIER
        if option in [0, 1, 2]:
            # 4x -> 4*x
            # a b -> a * b
            # a b c -> (a * b) * c
            node = Node('*', Leaf(values[0]), Leaf(values[1]))
            return node

        # rule: IDENTIFIER NUMBER
        if option == 3:
            # x4 -> x^4
            return Node('^', Leaf(values[0]), Leaf(values[1]))

        raise ParserSyntaxError('Unsupported option %d in target "%s".'
                                % (option, target))

    # -----------------------------------------
    # raw lex script, verbatim here
    # -----------------------------------------
    lexscript = r"""
    %{
    //int yylineno = 0;
    #include <stdio.h>
    #include <string.h>
    #include "Python.h"
    #define YYSTYPE void *
    #include "tokens.h"
    extern void *py_parser;
    extern void (*py_input)(PyObject *parser, char *buf, int *result, int max_size);
    #define returntoken(tok) yylval = PyString_FromString(strdup(yytext)); return (tok);
    #define YY_INPUT(buf,result,max_size) { (*py_input)(py_parser, buf, &result, max_size); }
    %}

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
    "quit"    { printf("lex: got QUIT\n"); yyterminate(); returntoken(QUIT); }
    "raise"   { returntoken(RAISE); }

    [ \t\v\f] {}
    [\n]      {yylineno++; returntoken(NEWLINE); }
    .         { printf("unknown char %c ignored, yytext=0x%lx\n", yytext[0], yytext); /* ignore bad chars */}

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
