from src.parser import Parser
from tests.parser import ParserWrapper
from src.possibilities import apply_suggestion


def validate(exp, result):
    """
    Validate that exp =>* result.
    """
    parser = ParserWrapper(Parser)
    result = parser.run([result])

    return traverse_preorder(parser, exp, result)


def traverse_preorder(parser, exp, result):
    """
    Traverse the possibility tree using pre-order traversal.
    """
    root = parser.run([exp])

    if root.equals(result):
        return root

    possibilities = parser.parser.possibilities

    for p in possibilities:
        child = apply_suggestion(root, p)
        next_root = traverse_preorder(parser, str(child), result)

        if next_root:
            return next_root
