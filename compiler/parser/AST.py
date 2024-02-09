
import sys
from typing import List
from dataclasses import dataclass

from compiler.parser.lexer import TokenType

"""
 PARSER AND CLASSES FOR AST

program = Program(function_definition)
function_definition = Function(identifier name, statement body)
statement = Return(exp) | Expression(exp) | Null
exp = Constant(int)
    | Var(identifier)
    | Unary(unary_operator, exp)
    | Binary(binary_operator, exp, exp)
    | Assignment(exp, exp)
unary_operator = Complement | Negate
binary_operator = Add | Subtract | Multiply | Divide | Remainder
declaration = Declaration(identifier name, exp? init)
"""


class bcolors:
    FAIL = '\033[91m'
    END = '\033[0m'


class ParseError(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        self.message = f"{bcolors.FAIL}ERROR (ParseError): Expected {self.expected} actual {self.actual}{bcolors.END}"
#        super().__init__(self.message)
        print(self.message)
        sys.exit()


class ParseErrorEmpty(Exception):
    def __init__(self):
        self.message = f"{bcolors.FAIL}ERROR (ParseError): The parser was empty before it was correctly parsed. Check if you are maybe missing a close brace or not.{bcolors.END}"
#        super().__init__(self.message)
        print(self.message)
        sys.exit()


class Binary:
    """Binary operation"""
    def __init__(self, binary_operator, exp, exp2) -> None:
        self.binary_operator = binary_operator
        # lhs
        self.exp1 = exp
        # rhs
        self.exp2 = exp2


@dataclass
class Binary_Operator:
    """Binary operation"""
    operator: TokenType
    operatorsList = [TokenType.PLUS_OPERATOR, TokenType.MULTIPLICATION_OPERATOR, TokenType.DIVISION_OPERATOR, TokenType.REMAINDER_OPERATOR, TokenType.UNARY_NEGATE, TokenType.NEQ_OPERATOR, TokenType.LTE_OPERATOR, TokenType.LT_OPERATOR, TokenType.GTE_OPERATOR, TokenType.GT_OPERATOR, TokenType.EQ_OPERATOR, TokenType.AND_OPERATOR, TokenType.OR_OPERATOR, TokenType.ASSIGNMENT_OPERATOR]


class Constant:
    """A constant value (example: int)"""
    def __init__(self, expint):
        self.int = int(expint)


class Var:
    """This is a variable name"""
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier


class Null(object):
    """Line with only ';'"""
    pass


class Unary_Operator:
    """Unary operator"""
    def __init__(self, operator) -> None:
        self.operator = operator


class Unary:
    """Unary operations"""
    def __init__(self, unary_operator, exp) -> None:
        self.unary_operator = unary_operator
        self.exp = exp


class ReturnStatement:
    """Unary statement"""
    def __init__(self, exp):
        self.exp = exp


# TO-DO: add Expression
class Statement:
    """A statement"""
    def __init__(self, statement) -> None:
        self.statement: Null | ReturnStatement = statement


class Declaration:
    """A variable declaration, example: int a = 0; int a;"""
    def __init__(self, name, init=None) -> None:
        self.name = name
        # If the variable is initialized in the same line that it is declared this willl be 1
        self.init = init


class Assignment:
    """A variable assignment (if a variable is declared and initialzed in same line this will be in the declaration.init) examples: int a = 0; a = 5;"""
    def __init__(self, left, right) -> None:
        self.left_exp = left
        self.right_exp = right


class FunctionDefinition:
    """Here is the body of the function the instructions and the name of the function"""
    """A function definition, example: int main()"""
    def __init__(self, name, body):
        self.name: str = name
        self.body: List[ReturnStatement | Declaration] = body


# in C we would use structs, in python we can use Classes
class Program:
    """The whole program stores all the functions"""
    def __init__(self, function_def):
        self.function_def: FunctionDefinition = function_def
