from node import ExpressionLeaf as Leaf

def get_factor_constants(operand):
    op = operand.title()
    res = []

    if operand.type == OP_MUL:
        if operand[0].type == LEAF_NUM:
            fn()

        if operand[1].type == LEAF_NUM:
            res += operand[1]

    return res

def combine_plus_factors(node):
    p = []

    # Check if any numeric factors can be combined
    def apply_numeric_factors(node, leaves):
        return Leaf(reduce(lambda a, b: a.value + b.value, leaves))

    num_nodes = []

    for n in node:
        # NUM + NUM -> NUM
        if n.type == VAL_NUM:
            num_nodes.append(n)

    if len(num_nodes) > 1:
        p.append((node, apply_plus_factors, num_nodes))

    # Check if any variable multiplcations/divisions can be combined
    def apply_identifiers(node, operands):
        apply_constant(lambda x: )
        return Leaf(leaves[0].value + leaves[1].value)

    id_nodes = []

    for n in node:
        # NUM *  + NUM -> NUM
        if n.type == OP_MUL:
            consts = get_factor_constants(n)

            if len(consts) > 1:
                id_nodes += 

    if len(num_nodes) > 1:
        p.append((node, apply_plus_factors, num_nodes))

    return p

rules = {
        '+': [combine_plus_factors],
        }
