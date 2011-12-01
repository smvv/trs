#class Expression(object):
#    """Class used to hold a mathematical expression."""
#
#    magic_operator_map = {
#            int.__add__: '%s + %s',
#            int.__sub__: '%s - %s',
#            int.__mul__: '%s * %s',
#            int.__div__: '%s / %s',
#            int.__neg__: '-%s',
#            int.__pow__: '%s**%s',
#            }
#
#    def __init__(self, operator, *args):
#        super(Expression, self).__init__()
#        self.operator, self.args = args[0], args[1:]
#
#    def __str__(self):
#        return self.magic_operator_map[self.operator] % self.args
