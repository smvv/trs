#!/usr/bin/python

def init_readline():
    import os
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

from src.parser import main

if __name__ == '__main__':
    init_readline()
    main()
