import sys
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

"""
 PARSER AND CLASSES FOR CODE
"""


class bcolors:
    FAIL = '\033[91m'
    END = '\033[0m'


class LexerError(Exception):
    def __init__(self):
        print("Error while parsing the error")
        sys.exit()


class TokenType(Enum):
    IDENTIFIER = auto()
    KEYWORD = auto()
    CONSTANT = auto()
    OPEN_PARENTHESIS = auto()
    CLOSE_PARENTHESIS = auto()
    UNARY_TILDE = auto()
    UNARY_NEGATE = auto()
    PLUS_OPERATOR = auto()
    ASSIGNMENT_OPERATOR = auto()
    MULTIPLICATION_OPERATOR = auto()
    DIVISION_OPERATOR = auto()
    REMAINDER_OPERATOR = auto()
    NOT_OPERATOR = auto()
    AND_OPERATOR = auto()
    OR_OPERATOR = auto()
    EQ_OPERATOR = auto()
    NEQ_OPERATOR = auto()
    LT_OPERATOR = auto()
    LTE_OPERATOR = auto()
    GT_OPERATOR = auto()
    GTE_OPERATOR = auto()
    OPEN_BRACE = auto()
    CLOSE_BRACE = auto()
    SEMICOLON = auto()


@dataclass
class Token:
    tok_type: TokenType
    tok_val: Optional[str | int] = None


class NewLexer:

    regexes = {
        (r'^[a-zA-Z_]\w*\b', 'IDENTIFIER'),
        (r'^[0-9]+\b', 'CONSTANT'),
        (r'^\(', 'OPEN_PARENTHESIS'),
        (r'^-', 'UNARY_NEGATE'),
        (r'^~', 'UNARY_TILDE'),
        (r'^\+', 'PLUS_OPERATOR'),
        (r'^\*', 'MULTIPLICATION_OPERATOR'),
        (r'^\/', 'DIVISION_OPERATOR'),
        (r'^\%', 'REMAINDER_OPERATOR'),
        (r'^\)', 'CLOSE_PARENTHESIS'),
        (r'^\!', 'NOT_OPERATOR'),
        (r'^&&', 'AND_OPERATOR'),
        (r'^\|\|', 'OR_OPERATOR'),
        (r'^==', 'EQ_OPERATOR'),
        (r'^\!=', 'NEQ_OPERATOR'),
        (r'^<', 'LT_OPERATOR'),
        (r'^>', 'GT_OPERATOR'),
        (r'^<=', 'LTE_OPERATOR'),
        (r'^>=', 'GTE_OPERATOR'),
        # (r'^&', 'BITWISE_AND'),
        # (r'^\|', 'BITWISE_OR'),
        # (r'^\^', 'BITWISE_XOR'),
        # (r'^<<', 'LEFT_SHIFT'),
        # (r'^>>', 'RIGHT_SHIFT'),
        (r'^{', 'OPEN_BRACE'),
        (r'^}', 'CLOSE_BRACE'),
        (r'^;', 'SEMICOLON'),
    }

    keyword_regexes = {
        (r'^int\b', 'INT_KEYWORD'),
        (r'^void\b', 'VOID_KEYWORD'),
        (r'^return\b', 'RETURN_KEYWORD'),
    }

    def __init__(self, source):
        self.source = source
        self.sourcelen = len(source)
        self.pointer = 0
        self.TOKENS = []
        if self.sourcelen == 0:
            print("The source file you gave is empty")
            sys.exit()

    def addToken(self, token, value: Optional[str | int] = None):
        if value is not None:
            self.TOKENS.append(Token(token, value))
        else:
            self.TOKENS.append(Token(token))

        # OLD
        # self.TOKENS.append({"type": token, "value": value})

    def readNumber(self):
        number = ""

        assert self.peek() is not None

        while str(self.peek()).isdigit():
            number = number + str(self.consume())
        self.addToken(TokenType.CONSTANT, int(number))

    def readIdentifier(self):
        setIdentifiers = {
            "int": "INT_KEYWORD",
            "void": "VOID_KEYWORD",
            "return": "RETURN_KEYWORD",
        }

        identifier = ""

        assert self.peek() is not None

        # we should also add digits so that we can check for variable names such as: var0
        while str(self.peek()).isalpha() or str(self.peek()) == "_" or str(self.peek()).isdigit():
            identifier = identifier + str(self.consume())

        if identifier in setIdentifiers:
            self.addToken(TokenType.KEYWORD, identifier)
        else:
            self.addToken(TokenType.IDENTIFIER, identifier)

    def startLexer(self):
        while self.peek() is not None:
            self.lex()

        return self.TOKENS

    def readComment(self):
        while self.peek() is not None and self.peek() != "\n":
            self.advance()
        self.advance()

    def lex(self):
        whitespace = [" ", "\t", "\n"]
        char = self.peek()
        match str(char):
            case "(":
                self.addToken(TokenType.OPEN_PARENTHESIS)
                self.advance()
            case "~":
                self.addToken(TokenType.UNARY_TILDE)
                self.advance()
            case "-":
                self.addToken(TokenType.UNARY_NEGATE)
                self.advance()
            case "+":
                self.addToken(TokenType.PLUS_OPERATOR)
                self.advance()
            case "*":
                self.addToken(TokenType.MULTIPLICATION_OPERATOR)
                self.advance()
            case "/":
                self.addToken(TokenType.DIVISION_OPERATOR)
                self.advance()
            case "%":
                self.addToken(TokenType.REMAINDER_OPERATOR)
                self.advance()
            case ")":
                self.addToken(TokenType.CLOSE_PARENTHESIS)
                self.advance()
            case "!":
                if self.peek_next() == "=":
                    self.addToken(TokenType.NEQ_OPERATOR)
                    self.advance(2)
                else:
                    self.addToken(TokenType.NOT_OPERATOR)
                    self.advance()
            case "<":
                if self.peek_next() == "=":
                    self.addToken(TokenType.LTE_OPERATOR)
                    self.advance(2)
                else:
                    self.addToken(TokenType.LT_OPERATOR)
                    self.advance()
            case ">":
                if self.peek_next() == "=":
                    self.addToken(TokenType.GTE_OPERATOR)
                    self.advance(2)
                else:
                    self.addToken(TokenType.GT_OPERATOR)
                    self.advance()
            case "&":
                if self.peek_next() == "&":
                    self.addToken(TokenType.AND_OPERATOR)
                    self.advance(2)
                else:
                    # later we can assign the bitwise operator here when it has been added
                    print("could not find any match with the lexer! only 1 &")
                    sys.exit()
            case "|":
                if self.peek_next() == "|":
                    self.addToken(TokenType.OR_OPERATOR)
                    self.advance(2)
                else:
                    # later we can assign the bitwise operator here when it has been added
                    print("could not find any match with the lexer! only 1 |")
                    sys.exit()
            case "=":
                if self.peek_next() == "=":
                    self.addToken(TokenType.EQ_OPERATOR)
                    self.advance(2)
                else:
                    self.addToken(TokenType.ASSIGNMENT_OPERATOR)
                    self.advance()
            case "{":
                self.addToken(TokenType.OPEN_BRACE)
                self.advance()
            case "}":
                self.addToken(TokenType.CLOSE_BRACE)
                self.advance()
            case ";":
                self.addToken(TokenType.SEMICOLON)
                self.advance()
            case value if value.isdigit():
                self.readNumber()
            case value if value.isalpha():
                self.readIdentifier()
            case value if value in whitespace:
                self.advance()
            case "/":
                if self.peek_next() == "/":
                    # this means this line is commented keep on going until the line is done
                    self.readComment()
                else:
                    self.advance()
            case _:
                print(value)
                print("Could not find any match with the lexer!")
                sys.exit()

    def peek(self):
        if self.pointer >= self.sourcelen:
            return None

        return self.source[self.pointer]

    def peek_next(self):
        if self.pointer + 1 > self.sourcelen:
            print("There aren't any characters left after this character")
            return None

        return self.source[self.pointer + 1]

    def peek_previous(self):
        if self.pointer - 1 < 0:
            print("This is the first character")
            return None

        return self.source[self.pointer - 1]

    def consume(self):
        current = self.source[self.pointer]
        self.advance()
        return current

    def advance(self, amount=None):
        if self.pointer > self.sourcelen:
            print("There aren't any characters left, not able to advance")
            return None

        if amount is None:
            amount = 1
        self.pointer += amount


def prettyPrinter(program):
    print(f"""
Program(
    Function (
        name="{program.function_def.name}",
        body=Return (
            Constant({program.function_def.body.exp.int})
        )
    )
)""")
