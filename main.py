#!/usr/bin/python
"""
Shell front-end for the mathematical term rewriting system. This shell will
parse mathematical expressions into an expression tree, produce possible
rewrite steps and, if requested, provide a hint to rewrite the last entered
expression.
"""

import argparse
import sys
import os

from src.backend.backend import app


def init_readline():
    try:
        import readline
    except ImportError:
        return

    histfile = os.path.join(os.path.expanduser("~"), ".trs_hist")

    try:
        readline.read_history_file(histfile)
    except IOError:
        pass

    import atexit
    atexit.register(readline.write_history_file, histfile)


def get_args():
    parser = argparse.ArgumentParser(prog='trs', description=__doc__)

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
    parser.add_argument('--interactive', action='store_true',
            default=sys.stdin.isatty(),
            help='Enable interactive mode (default). This is the inverse of' \
                 ' --batch.')
    parser.add_argument('--backend', action='store_true',
            default=False,
            help='Start term rewriting system backend (default: disabled).' \
                 ' This is the backend for the web frontend.')
    parser.add_argument('port', type=int, default=8080, nargs='?',
            help='Port number for system backend (default: 8080).')

    return parser.parse_args()


def main():
    from src.parser import Parser

    args = get_args()

    if args.backend:
        sys.argv[1] = str(args.port)
        return app.run()

    interactive = args.interactive and not args.batch

    p = Parser(verbose=args.verbose,
               keepfiles=args.keepfiles,
               interactive=interactive)

    node = p.run(debug=args.debug)

    # Clear the line, when the shell exits.
    if interactive:
        print

    return node


if __name__ == '__main__':
    init_readline()
    main()
