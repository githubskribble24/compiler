class Program:

    def __init__(self, function_definition):
        self.function_definition = function_definition


class function_Def:

    def __init__(self, identifier, instructions):
        self.name = identifier
        self.body = instructions


class Tacky_Unary_Operator:

    def __init__(self, tacky_op):
        self.operator = tacky_op


class Not:
    pass


class Complement:
    pass


class Negate:
    pass


class Binary_Operator:

    def __init__(self, binary_operator) -> None:
        self.operator = binary_operator


class Add:
    pass


class Subtract:
    pass


class Multiply:
    pass


class Divide:
    pass


class Remainder:
    pass


class Equal:
    pass


class NotEqual:
    pass


class LessThan:
    pass


class LessOrEqual:
    pass


class GreaterThan:
    pass


class GreaterOrEqual:
    pass


# INSTRUCTIONS
class Binary:
    def __init__(self, binary_operator, src1, src2, dst) -> None:
        self.operator = binary_operator
        self.src1 = src1
        self.src2 = src2
        self.dst = dst


class UnaryTacky:

    def __init__(self, tacky_op, src, dst) -> None:
        self.unary_operator = tacky_op
        self.src = src
        self.dst = dst


class Copy:
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst


class Jump:
    def __init__(self, target) -> None:
        self.target = target


class JumpIfZero:
    def __init__(self, condition, target) -> None:
        self.target = target
        self.condition = condition


class JumpIfNotZero:
    def __init__(self, condition, target) -> None:
        self.target = target
        self.condition = condition


class Label:
    def __init__(self, identifier) -> None:
        self.identifier = identifier


class Return:

    def __init__(self, value):
        self.val = value


class Var:

    def __init__(self, name):
        self.name = name


class Constant:

    def __init__(self, int):
        self.int = int
