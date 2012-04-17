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
