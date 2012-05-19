from parser import Parser
from possibilities import apply_suggestion
from strategy import find_possibilities
from tests.parser import ParserWrapper


def validate(exp, result):
    """
    Validate that exp =>* result.
    """
    parser = ParserWrapper(Parser)

    exp = parser.run([exp])
    result = parser.run([result])

    # Compare the simplified expressions first, in order to avoid the
    # computational intensive traversal of the possibilities tree.
    parser.set_root_node(exp)
    a = parser.rewrite_all()

    parser.set_root_node(result)
    b = parser.rewrite_all()

    if not a or not a.equals(b):
        return False

    # TODO: make sure cycles are avoided / eliminated using cycle detection.
    def traverse_preorder(node, result):
        if node.equals(result):
            return True

        for p in find_possibilities(node):
            # Clone the root node because it will be used in multiple
            # substitutions
            child = apply_suggestion(node.clone(), p)

            if traverse_preorder(child, result):
                return True

        return False

    return traverse_preorder(exp, result)
