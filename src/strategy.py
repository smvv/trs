from node import OP_NEG
from rules import RULES
from rules.precedences import HIGH, LOW, RELATIVE


def compare_possibilities(a, b):
    """
    Comparable function for (possibility, depth) pairs.
    Returns a positive number if A has a lower priority than B, a negative
    number for the reverse case, and 0 if the possibilities have equal
    priorities.
    """
    (pa, da), (pb, db) = a, b
    ha, hb = pa.handler, pb.handler

    # Check if A and B have a precedence relative to eachother
    if (ha, hb) in RELATIVE:
        return -1

    if (hb, ha) in RELATIVE:
        return 1

    # If A has a high priority, it might be moved to the start of the list
    if ha in HIGH:
        # Id B has a high priority too, compare the positions in the list
        if hb in HIGH:
            return HIGH[ha] - HIGH[hb]

        # Move A towards the beginning of the list
        return -1

    # If only B has a high priority, move it up with respect to A
    if hb in HIGH:
        return 1

    # If A has a low priority, it might be moved to the end of the list
    if ha in LOW:
        # Id B has a low priority too, compare the positions in the list
        if hb in LOW:
            return LOW[ha] - LOW[hb]

        # Move A towards the end of the list
        return 1

    # If only B has a high priority, move it down with respect to A
    if hb in LOW:
        return -1

    # default: use order that was generated implicitely by leftmost-innermost
    # expression traversal
    return 0


def depth_possibilities(node, depth=0, parent_op=None):
    p = []
    handlers = []

    # Add operator-specific handlers
    if not node.is_leaf:
        # Traverse through child nodes first using postorder traversal
        for child in node:
            # FIXME: "depth + 1" is disabled for the purpose of
            #        leftmost-innermost traversal
            p += depth_possibilities(child, depth, node.op)

        # Add operator-specific handlers. Prevent duplicate possibilities in
        # n-ary nodes by only executing the handlers on the outermost node of
        # related nodes with the same operator
        if node.op != parent_op and node.op in RULES:
            handlers += RULES[node.op]

    # Add negation handlers after operator-specific handlers to obtain an
    # outermost effect for negations
    if node.negated:
        handlers += RULES[OP_NEG]

    # Run handlers
    for handler in handlers:
        p += [(pos, depth) for pos in handler(node)]

    #print node, p
    return p


def find_possibilities(node):
    """
    Find all possibilities inside a node and return them in a list.
    """
    possibilities = depth_possibilities(node)
    #import copy
    #old_possibilities = copy.deepcopy(possibilities)
    possibilities.sort(compare_possibilities)
    #get_handler = lambda (p, d): str(p.handler)
    #if old_possibilities != possibilities:
    #    print 'before:', '\n    '.join(map(get_handler, old_possibilities))
    #    print 'after:', '\n    '.join(map(get_handler, possibilities))

    return [p for p, depth in possibilities]

# 2x ^ 2 = 3x ^ (1 + 1)
