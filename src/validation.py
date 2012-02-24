from src.parser import Parser
from tests.parser import ParserWrapper


class ValidationNode(object):
    pass


def validate(exp, result):
    """
    Validate that exp =>* result.
    """
    parser = ParserWrapper(Parser)

    exp = parser.run([exp])
    result = parser.run([result])

    return validate_graph(exp, result)


def iter_preorder(exp, possibility):
    """
    Traverse the possibility tree using pre-order traversal.
    """
    pass


def validate_graph(exp, result):
    """
    Validate that "exp" =>* "result".
    """
    # TODO: Traverse the tree of possibility applications
    return False
