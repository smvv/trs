"""
This parser will parse the given input and build an expression tree. Grammar
file for the supported mathematical expressions.
"""

import os.path
PYBISON_BUILD = os.path.realpath('build/external/pybison')
EXTERNAL_MODS = os.path.realpath('external')

import sys
sys.path.insert(0, PYBISON_BUILD)
sys.path.insert(1, EXTERNAL_MODS)

from pybison import BisonParser, BisonSyntaxError
from graph_drawing.graph import generate_graph

from node import ExpressionNode as Node, ExpressionLeaf as Leaf, OP_MAP, \
        OP_DER, TOKEN_MAP, TYPE_OPERATOR, OP_COMMA, OP_NEG, OP_MUL, OP_DIV, \
        OP_LOG, OP_ADD, Scope, E, DEFAULT_LOGARITHM_BASE, OP_VALUE_MAP, \
        SPECIAL_TOKENS
from rules import RULES
from strategy import pick_suggestion
from possibilities import filter_duplicates, apply_suggestion

import Queue
import re


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

    # Words to be ignored by preprocessor
    words = zip(*filter(lambda (s, op): TOKEN_MAP[op] == 'FUNCTION', \
                             OP_MAP.iteritems()))[0] \
            + ('raise', 'graph') + tuple(SPECIAL_TOKENS)

    # Output directory of generated pybison files, including a trailing slash.
    buildDirectory = PYBISON_BUILD + '/'

    # ----------------------------------------------------------------
    # lexer tokens - these must match those in your lex script (below)
    # ----------------------------------------------------------------
    # TODO: add a runtime check to verify that this token list match the list
    # of tokens of the lex script.
    tokens = ['NUMBER', 'IDENTIFIER', 'NEWLINE', 'QUIT', 'RAISE', 'GRAPH',
              'LPAREN', 'RPAREN', 'FUNCTION', 'FUNCTION_LPAREN', 'LBRACKET',
              'RBRACKET', 'APOSTROPH', 'DERIVATIVE'] \
             + filter(lambda t: t != 'FUNCTION', TOKEN_MAP.values())

    # ------------------------------
    # precedences
    # ------------------------------
    precedences = (
        ('left', ('COMMA', )),
        ('left', ('MINUS', 'PLUS')),
        ('left', ('TIMES', 'DIVIDE')),
        ('right', ('FUNCTION', 'DERIVATIVE')),
        ('left', ('EQ', )),
        ('left', ('NEG', )),
        ('right', ('POW', )),
        ('right', ('FUNCTION_LPAREN', )),
        )

    interactive = 0

    def __init__(self, **kwargs):
        BisonParser.__init__(self, **kwargs)
        self.interactive = kwargs.get('interactive', 0)
        self.timeout = kwargs.get('timeout', 0)

        self.reset()

    def reset(self):
        self.read_buffer = ''
        self.read_queue = Queue.Queue()

        #self.subtree_map = {}
        self.root_node = None
        self.possibilities = self.last_possibilities = []

    def run(self, *args, **kwargs):
        self.reset()
        return super(Parser, self).run(*args, **kwargs)

    # Override default read method with a version that prompts for input.
    def read(self, nbytes):
        if self.file == sys.stdin and self.file.closed:
            return ''

        if not self.read_buffer and not self.read_queue.empty():
            self.read_buffer = self.read_queue.get_nowait() + '\n'

        if self.read_buffer:
            read_buffer = self.read_buffer[:nbytes]

            self.read_buffer = self.read_buffer[nbytes:]
            return read_buffer

        try:
            read_buffer = raw_input('>>> ' if self.interactive else '') + '\n'
        except EOFError:
            return ''

        self.read_buffer = read_buffer[nbytes:]
        return read_buffer[:nbytes]

    def hook_read_before(self):
        if self.possibilities:
            if self.verbose:  # pragma: nocover
                print 'possibilities:'

            items = filter_duplicates(self.possibilities)
            self.last_possibilities = self.possibilities

            if self.verbose:  # pragma: nocover
                print '  ' + '\n  '.join(map(str, items))

    def hook_read_after(self, data):
        """
        This hook will be called when the read() method returned. The data
        argument points to the data read by the read() method. This hook
        function should return the data to be used by the parser.
        """
        if not data.strip():
            return data

        self.possibilities = []

        # Replace known keywords with escape sequences.
        words = list(self.__class__.words)
        words.insert(10, '\n')

        for i, keyword in enumerate(words):
            # FIXME: Why case-insensitivity?
            data = re.sub(keyword, chr(i), data, flags=re.I)

        # TODO: remove this quick preprocessing hack. This hack enables
        # concatenated expressions, since the grammar currently does not
        # support those. This workaround will replace:
        #   - ")(" with ")*(".
        #   - "a(" with "a*(".
        #   - ")a" with ")*a".
        #   - "ab" with "a*b".
        #   - "4a" with "4*a".
        #   - "a4" with "a^4".

        pattern = ('(?:(\))\s*(\()'                       # )(  -> ) * (
                + '|(\))\s*(\[)'                          # )[  -> ) * [
                + '|([\x00-\x09\x0b-\x19a-z0-9])\s*(\()'  # a(  -> a * (
                + '|(\))\s*([\x00-\x09\x0b-\x19a-z0-9])'  # )a  -> ) * a
                + '|([\x00-\x09\x0b-\x19a-z])\s*'
                  + '([\x00-\x09\x0b-\x19a-z])'           # ab  -> a * b
                + '|([0-9])\s*([\x00-\x09\x0b-\x19a-z])'  # 4a  -> 4 * a
                + '|([\x00-\x09\x0b-\x19a-z])\s*([0-9])'  # a4  -> a ^ 4
                + '|([0-9])\s+([0-9]))'                   # 4 4 -> 4 * 4
                )

        def preprocess_data(match):
            left, right = filter(None, match.groups())

            # Make sure there are no multiplication and exponentiation signs
            # inserted between a function and its argument(s): "sin x" should
            # not be written as "sin*x", because that is bogus.
            if ord(left) <= 0x9 or 0x0b <= ord(left) <= 0x19:
                return left + ' ' + right

            # If all characters on the right are numbers. e.g. "a4", the
            # expression implies exponentiation. Make sure ")4" is not
            # converted into an exponentiation, because that's multiplication.
            if left != ')' and not 48 <= ord(left) < 58 \
                    and all(map(lambda x: 48 <= ord(x) < 58, list(right))):
                return '%s^%s' % (left, right)

            # match: ab | abc | abcd (where left = "a")
            return '*'.join([left] + list(right))

        if self.verbose:  # pragma: nocover
            data_before = data

        # Iteratively replace all matches.
        i = 0

        while i < len(data):
            data = data[:i] + re.sub(pattern, preprocess_data, data[i:])
            i += 1

        # Replace escape sequences with original keywords.
        for i, keyword in enumerate(words):
            data = data.replace(chr(i), keyword)

        if self.verbose and data_before != data:  # pragma: nocover
            print 'hook_read_after() modified the input data:'
            print 'before:', repr(data_before)
            print 'after :', repr(data)

        return data

    def hook_handler(self, target, option, names, values, retval):
        if target in ['exp', 'line', 'input'] or not retval:
            return retval

        if not retval.negated and retval.type != TYPE_OPERATOR:
            return retval

        if retval.type == TYPE_OPERATOR and retval.op in RULES:
            handlers = RULES[retval.op]
        else:
            handlers = []

        if retval.negated:
            handlers = RULES[OP_NEG]

        for handler in handlers:
            possibilities = handler(retval)
            self.possibilities.extend(possibilities)

        return retval

    def display_hint(self):
        print pick_suggestion(self.last_possibilities)

    def display_possibilities(self):
        if self.last_possibilities:
            print '\n'.join(map(str, self.last_possibilities))

    def rewrite(self):
        suggestion = pick_suggestion(self.last_possibilities)

        if self.verbose:
            print 'applying suggestion:', suggestion

        if not suggestion:
            return self.root_node

        expression = apply_suggestion(self.root_node, suggestion)

        if self.verbose:
            print 'After application, expression=', expression

        self.read_queue.put_nowait(str(expression))

        return expression

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
              | input REWRITE NEWLINE
        """
        if option == 1:
            # Interactive mode is enabled if the term rewriting system is used
            # as a shell. In that case, it is useful that the shell prints the
            # output of the evaluation.
            if self.interactive and values[1]:  # pragma: nocover
                print values[1]

            return values[1]

        if option == 2:  # rule: input REWRITE NEWLINE
            self.root_node = self.rewrite()
            return self.root_node

    def on_line(self, target, option, names, values):
        """
        line : NEWLINE
             | exp NEWLINE
             | debug NEWLINE
             | HINT NEWLINE
             | POSSIBILITIES NEWLINE
             | RAISE NEWLINE
        """
        if option == 1:  # rule: EXP NEWLINE
            self.root_node = values[0]

            # Clear list of last possibilities when current expression has no
            # possibilities. Otherwise, an invalid expression gets the last
            # possibilities of a valid expression.
            if not self.possibilities:
                self.last_possibilities = []

            return values[0]

        if option == 2:  # rule: DEBUG NEWLINE
            self.root_node = values[0]
            return values[0]

        if option == 3:  # rule: HINT NEWLINE
            self.display_hint()
            return

        if option == 4:  # rule: POSSIBILITIES NEWLINE
            self.display_possibilities()
            return

        if option == 5:
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

        if 3 <= option <= 5:  # rule: unary | binary | nary
            return values[0]

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_unary(self, target, option, names, values):
        """
        unary : MINUS exp %prec NEG
              | FUNCTION_LPAREN exp RPAREN
              | FUNCTION exp
              | DERIVATIVE exp
              | bracket_derivative
        """

        if option == 0:  # rule: NEG exp
            node = values[1]
            # Add negation to the left-most child
            if node.is_leaf or (node.op != OP_MUL and node.op != OP_DIV):
                node.negated += 1
            else:
                child = Scope(node)[0]
                child.negated += 1

            return node

        if option in (1, 2):  # rule: FUNCTION_LPAREN exp RPAREN | FUNCTION exp
            op = values[0].split(' ', 1)[0]

            if op == 'ln':
                return Node(OP_LOG, values[1], Leaf(E))

            if values[1].is_op(OP_COMMA):
                return Node(op, *values[1])

            if op == OP_VALUE_MAP[OP_LOG]:
                return Node(OP_LOG, values[1], Leaf(DEFAULT_LOGARITHM_BASE))

            m = re.match(r'^log_([0-9]+|[a-zA-Z])', op)

            if m:
                value = m.group(1)

                if value.isdigit():
                    value = int(value)

                return Node(OP_LOG, values[1], Leaf(value))

            return Node(op, values[1])

        if option == 3:  # rule: DERIVATIVE exp
            # DERIVATIVE looks like 'd/d*x*' -> extract the 'x'
            return Node(OP_DER, values[1], Leaf(values[0][-2]))

        if option == 4:  # rule: bracket_derivative
            return values[0]

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_bracket_derivative(self, target, option, names, values):
        """
        bracket_derivative : LBRACKET exp RBRACKET APOSTROPH
                           | bracket_derivative APOSTROPH
        """

        if option == 0:  # rule: LBRACKET exp RBRACKET APOSTROPH
            return Node(OP_DER, values[1])

        if option == 1:  # rule: bracket_derivative APOSTROPH
            return Node(OP_DER, values[0])

        raise BisonSyntaxError('Unsupported option %d in target "%s".'
                               % (option, target))  # pragma: nocover

    def on_binary(self, target, option, names, values):
        """
        binary : exp PLUS exp
               | exp TIMES exp
               | exp DIVIDE exp
               | exp POW exp
               | exp EQ exp
               | exp MINUS exp
        """

        if 0 <= option < 5:  # rule: exp {PLUS,TIMES,DIVIDES,POW,EQ} exp
            return Node(values[1], values[0], values[2])

        if option == 5:  # rule: exp MINUS exp
            node = values[2]

            # Add negation to the left-most child
            if node.is_leaf or (node.op != OP_MUL and node.op != OP_DIV):
                node.negated += 1
            else:
                node = Scope(node)[0]
                node.negated += 1

            # Explicit call the hook handler on the created unary negation.
            node = self.hook_handler('binary', 4, names, values, node)

            return Node(OP_ADD, values[0], values[2])

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
    # Special tokens and operator tokens
    # -----------------------------------------
    operators = ''
    functions = []

    for token in SPECIAL_TOKENS:
        operators += '"%s"%s{ returntoken(IDENTIFIER); }\n' \
                     % (token, ' ' * (8 - len(token)))

    for op_str, op in OP_MAP.iteritems():
        if TOKEN_MAP[op] == 'FUNCTION':
            functions.append(op_str)
        else:
            operators += '"%s"%s{ returntoken(%s); }\n' \
                         % (op_str, ' ' * (8 - len(op_str)), TOKEN_MAP[op])

    # Put all functions in a single regex
    if functions:
        operators += '("%s")[ ]*"(" { returntoken(FUNCTION_LPAREN); }\n' \
                     % '"|"'.join(functions)
        operators += '("%s") { returntoken(FUNCTION); }\n' \
                     % '"|"'.join(functions)

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
    %}

    %option yylineno

    %%

    d[ ]*"/"[ ]*"d*"[a-z]"*" { returntoken(DERIVATIVE); }
    [0-9]+"."?[0-9]* { returntoken(NUMBER); }
    [a-zA-Z]  { returntoken(IDENTIFIER); }
    "("       { returntoken(LPAREN); }
    ")"       { returntoken(RPAREN); }
    "["       { returntoken(LBRACKET); }
    "]"       { returntoken(RBRACKET); }
    "'"       { returntoken(APOSTROPH); }
    log_([0-9]+|[a-zA-Z])"*(" { returntoken(FUNCTION_LPAREN); }
    log_([0-9]+|[a-zA-Z])"*" { returntoken(FUNCTION); }
    """ + operators + r"""
    "raise"   { returntoken(RAISE); }
    "graph"   { returntoken(GRAPH); }
    "quit"    { yyterminate(); returntoken(QUIT); }

    [ \t\v\f] { }
    [\n]      { yycolumn = 0; returntoken(NEWLINE); }
    .         { printf("unknown char %c ignored.\n", yytext[0]); }

    %%

    yywrap() { return(1); }
    """
