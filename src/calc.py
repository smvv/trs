#!/usr/bin/env python
"""
A simple pybison parser program implementing a calculator
"""

from __future__ import division
from sympy import Symbol
from logger import filter_non_ascii

import os.path
PYBISON_BUILD = os.path.realpath('build/external/pybison')
PYBISON_PYREX = os.path.realpath('external/pybison/src/pyrex')

import sys
sys.path.insert(0, PYBISON_BUILD)
sys.path.insert(1, PYBISON_PYREX)

from bison import BisonParser, BisonNode

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
    tokens = ['NUMBER', 'IDENTIFIER',
              'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POW',
              'LPAREN', 'RPAREN',
              'NEWLINE', 'QUIT']

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
            return raw_input('>>> ') + "\n"
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
    start = "input"

    def on_input(self, target, option, names, values):
        """
        input :
              | input line
        """

        if option == 1:
            # Interactive mode is enabled if the term rewriting system is used
            # as a shell. In that case, it is useful that the shell prints the
            # output of the evaluation.
            if self.interactive:
                print values[1]

            return values[1]

    def on_line(self, target, option, names, values):
        """
        line : NEWLINE
             | exp NEWLINE
        """
        if option in [1, 2]:
            if self.verbose:
                print 'on_line: exp =', values[0]

            return values[0]

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

        if self.verbose:
            print 'on_exp: got %s %s %s %s' % (target, option, names, values)

        # rule: NUMBER
        if option == 0:
            # TODO: A bit hacky, this achieves long integers and floats.
            #return float(values[0]) if '.' in values[0] else long(values[0])
            #return float(values[0])
            return float(values[0]) if '.' in values[0] else int(values[0])

        # rule: IDENTIFIER
        if option == 1:
            return Symbol(values[0])

        # rule: LPAREN exp RPAREN
        if option == 8:
            return values[1]

        # rule: symbolic
        if option == 9:
            return values[1]

        try:
            # rule: exp PLUS expo
            if option == 2:
                return values[0] + values[2]

            # rule: exp MINUS expo
            if option == 3:
                return values[0] - values[2]

            # rule: exp TIMES expo
            if option == 4:
                return values[0] * values[2]

            # rule: exp DIVIDE expo
            if option == 5:
                return values[0] / values[2]

            # rule: NEG expo
            if option == 6:
                return - values[1]

            # rule: exp POW expo
            if option == 7:
                return values[0] ** values[2]
        except OverflowError:
            print >>sys.stderr, 'error: Overflow occured in "%s" %s %s %s' \
                                % (target, option, names, values)

    def on_symbolic(self, target, option, names, values):
        """
        symbolic : NUMBER IDENTIFIER
                 | IDENTIFIER NUMBER
                 | IDENTIFIER IDENTIFIER
        """
        # TODO: this class method requires verification.

        # rule: NUMBER IDENTIFIER
        if option == 0:
            # 4x -> 4*x
            return values[0] * Symbol(values[1])

        # rule: IDENTIFIER NUMBER
        if option == 1:
            # x4 -> x^4
            return Symbol(values[0]) ** values[1]

        # rule: IDENTIFIER IDENTIFIER
        if option == 2:
            # a b -> a * b
            return Symbol(values[0]) * Symbol(values[1])

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

    [0-9]+ { returntoken(NUMBER); }
    [a-zA-Z][a-zA-Z0-9]* { returntoken(IDENTIFIER); }
    "("    { returntoken(LPAREN); }
    ")"    { returntoken(RPAREN); }
    "+"    { returntoken(PLUS); }
    "-"    { returntoken(MINUS); }
    "*"    { returntoken(TIMES); }
    "^"    { returntoken(POW); }
    "/"    { returntoken(DIVIDE); }
    "quit" { printf("lex: got QUIT\n"); yyterminate(); returntoken(QUIT); }

    [ \t\v\f]             {}
    [\n]		{yylineno++; returntoken(NEWLINE); }
    .       { printf("unknown char %c ignored, yytext=0x%lx\n", yytext[0], yytext); /* ignore bad chars */}

    %%

    yywrap() { return(1); }
    """

if __name__ == '__main__':
    p = Parser(verbose=0, keepfiles=1, interactive=1)
    p.run(debug=0)

    # Clear the line, when the shell exits.
    print
