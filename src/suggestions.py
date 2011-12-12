#!/usr/bin/env python
from parser import main
from node import ExpressionLeaf as Leaf
from rules import rules

# (node, funcptr, (args...))


def get_node_possibilities(node):
    """
    Get all possible rewrite steps for this node.
    """
    op = node.title()
    possibilities = []

    for key, fn in rules.iteritems():
        if op == key:
            possibilities += fn(node)

    return possibilities


def get_possibilities(node):
    """
    Get all possible rewrite steps for this node and its children.
    """
    possibilities = get_node_possibilities(node)

    if not isinstance(node, Leaf):
        possibilities += [get_possibilities(n) for n in node]

    return possibilities


if __name__ == '__main__':
    node = main()
    print 'node:', node

    p = get_possibilities(node)
    print ' p: -------------'
    print '\n'.join(p),
    print '----------------'
