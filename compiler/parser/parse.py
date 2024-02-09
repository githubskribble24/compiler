import sys

from compiler.parser.lexer import TokenType
from compiler.parser.AST import (
    ReturnStatement,
    Unary,
    Unary_Operator,
    Binary_Operator,
    Constant,
    Var,
    Assignment,
    Binary,
    Declaration,
    Null,
    FunctionDefinition,
    Program
)


class bcolors:
    FAIL = '\033[91m'
    END = '\033[0m'


class ParseError(Exception):
    """Error while parsing"""
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        self.message = f"{bcolors.FAIL}ERROR (ParseError): Expected {self.expected} actual {self.actual}{bcolors.END}"
        print(self.message)
        sys.exit()


class ParseErrorFactor(Exception):
    """Unknown factor found"""
    def __init__(self, expected):
        self.message = f"{bcolors.FAIL}ERROR (ParseErrorFactor): Malformed factor last Token: {expected}{bcolors.END}"
        print(self.message)
        sys.exit()


class ParseErrorExp(Exception):
    """Unknown expression found"""
    def __init__(self, expected, actual):
        self.message = f"{bcolors.FAIL}ERROR (ParseErrorExp): Malformed exp last Token: {expected}{bcolors.END}"
        print(self.message)
        sys.exit()


class ParseErrorPrec(Exception):
    """Unknown token type found while parsing"""
    def __init__(self, actual):
        self.message = f"{bcolors.FAIL}ERROR (ParseErrorPrec): Gotten a wrong Token type when trying to get the precedence value of a token, gotten the Token: {actual}{bcolors.END}"
        print(self.message)
        sys.exit()


class ParseErrorEmpty(Exception):
    """Empty parser."""
    def __init__(self):
        self.message = f"{bcolors.FAIL}ERROR (ParseError): The parser was empty before it was correctly parsed. Check if you are maybe missing a close brace or not.{bcolors.END}"
        print(self.message)
        sys.exit()


def expect(expectedType, tokens):
    if len(tokens) == 0:
        raise ParseErrorEmpty()

    actualToken = tokens.pop(0)
    if type(expectedType) is str:
        if actualToken.tok_val != expectedType:
            raise ParseError(expectedType, actualToken.tok_val)
    elif isinstance(expectedType, TokenType):
        if actualToken.tok_type != expectedType:
            raise ParseError(expectedType, actualToken.tok_val)
    else:
        print("WRONG INFO")
        sys.exit()

    return tokens


def peek_next_token(tokens):
    return tokens[1]


def parse_unop(tokens):
    this_token = tokens.pop(0)
    if this_token.tok_type is not TokenType.UNARY_NEGATE and this_token.tok_type is not TokenType.UNARY_TILDE and this_token.tok_type is not TokenType.NOT_OPERATOR:
        raise ParseError("UNARY OPERATOR", this_token.tok_type)

    operator = Unary_Operator(this_token.tok_type)

    return [operator, tokens]


def parse_binop(tokens):
    this_token = tokens.pop(0)

    if this_token.tok_type not in Binary_Operator.operatorsList:
        raise ParseError("A Binary_Operator", this_token.tok_type)

    operator = Binary_Operator(this_token.tok_type)

    return [operator, tokens]


def parse_factor(tokens):
    this_token = tokens[0]
    # next_token = peek_next_token(tokens)
    # print(f"\n\n\nNext token: {next_token}\n\n\n")
    if this_token.tok_type is TokenType.CONSTANT:
        expression = Constant(this_token.tok_val)
        tokens.pop(0)
        return [expression, tokens]

    elif this_token.tok_type is TokenType.UNARY_TILDE or this_token.tok_type is TokenType.UNARY_NEGATE or this_token.tok_type is TokenType.NOT_OPERATOR:
        unary_operator, tokens = parse_unop(tokens)
        inner_factor, tokens = parse_factor(tokens)
        return [Unary(unary_operator, inner_factor), tokens]

    elif this_token.tok_type is TokenType.OPEN_PARENTHESIS:
        tokens.pop(0)
        inner_exp, tokens = parse_exp(tokens, 0)
        tokens = expect(TokenType.CLOSE_PARENTHESIS, tokens)
        return [inner_exp, tokens]

    elif this_token.tok_type is TokenType.IDENTIFIER:
        token = tokens.pop(0)
        return [Var(token.tok_val), tokens]

    else:
        raise ParseErrorFactor(this_token.tok_val)


# Recursive function
def parse_exp(tokens, min_prec):
    left, tokens = parse_factor(tokens)
    next_token = tokens[0]
    # check if the token after the const/exp (left) is a binary operator or not (checks for "+" and "-")
    while (next_token.tok_type in Binary_Operator.operatorsList) and precedenceOfToken(next_token) >= min_prec:

        # double check to make sure if a Binary operator is inside of here
        assert next_token.tok_type in Binary_Operator.operatorsList

        if next_token.tok_type is TokenType.ASSIGNMENT_OPERATOR:
            tokens.pop(0)  # Remove the assignment operator from the list of tokens
            right, tokens = parse_exp(tokens, precedenceOfToken(next_token))
            left = Assignment(left, right)
        else:
            operator, tokens = parse_binop(tokens)
            right, tokens = parse_exp(tokens, precedenceOfToken(next_token) + 1)
            left = Binary(operator, left, right)

        next_token = tokens[0]
    return [left, tokens]


def precedenceOfToken(token):
    type = token.tok_type
    match type:
        case (TokenType.MULTIPLICATION_OPERATOR | TokenType.DIVISION_OPERATOR | TokenType.REMAINDER_OPERATOR):
            return 50
        case (TokenType.PLUS_OPERATOR | TokenType.UNARY_NEGATE):
            return 45
        case (TokenType.LT_OPERATOR | TokenType.LTE_OPERATOR | TokenType.GT_OPERATOR | TokenType.GTE_OPERATOR):
            return 35
        case (TokenType.EQ_OPERATOR | TokenType.NEQ_OPERATOR):
            return 30
        case TokenType.AND_OPERATOR:
            return 10
        case TokenType.OR_OPERATOR:
            return 5
        case TokenType.ASSIGNMENT_OPERATOR:
            return 1
        case _:
            print(type)
            raise ParseErrorPrec(type)


def peek(tokens):
    return tokens[0]


def parse_statement(tokens):
    if peek(tokens).tok_val == "return":
        tokens = expect("return", tokens)
        exp, tokens = parse_exp(tokens, 0)
        tokens = expect(TokenType.SEMICOLON, tokens)

        return [ReturnStatement(exp), tokens]
    elif peek(tokens).tok_type is TokenType.SEMICOLON:
        tokens = expect(TokenType.SEMICOLON, tokens)

        return [Null(), tokens]
    else:
        exp, tokens = parse_exp(tokens, 0)
        tokens = expect(TokenType.SEMICOLON, tokens)
        return [exp, tokens]


def parse_declaration(tokens):
    tokens = expect("int", tokens)
    identifier, tokens = parse_identifier(tokens)

    token = tokens.pop(0)
    if token.tok_type is TokenType.ASSIGNMENT_OPERATOR:
        exp, tokens = parse_exp(tokens, precedenceOfToken(token))
        tokens = expect(TokenType.SEMICOLON, tokens)
        return [Declaration(identifier, exp), tokens]
    elif token.tok_type is TokenType.SEMICOLON:
        # this is only a declared variable not initialized
        return [Declaration(identifier), tokens]
    else:
        print("DID NOT GET THE RIGHT DECLARATION STOPPED BECAUSE OF THAT")
        print(f"We got the token type: {token.tok_type}, with the value: {token.tok_val}")
        sys.exit()


def parse_block_item(tokens):
    current_token = peek(tokens)
    block_items = []
    while current_token.tok_type is not TokenType.CLOSE_BRACE:
        if current_token.tok_val == "int":
            declaration, tokens = parse_declaration(tokens)
            block_items.append(declaration)
        else:
            statement, tokens = parse_statement(tokens)
            block_items.append(statement)

        current_token = peek(tokens)

    return [block_items, tokens]


def parse_identifier(tokens):
    token = tokens.pop(0)
    if token.tok_type != TokenType.IDENTIFIER:
        raise ParseError("IDENTIFIER", token.tok_type)
    return [token.tok_val, tokens]


# Parse function_definition
def Parser(tokens):
    while True:
        tokens = expect("int", tokens)
        fun_name, tokens = parse_identifier(tokens)

        tokens = expect(TokenType.OPEN_PARENTHESIS, tokens)
        tokens = expect("void", tokens)
        tokens = expect(TokenType.CLOSE_PARENTHESIS, tokens)
        tokens = expect(TokenType.OPEN_BRACE, tokens)

        function_body, tokens = parse_block_item(tokens)
        tokens = expect(TokenType.CLOSE_BRACE, tokens)
        break

    return Program(FunctionDefinition(fun_name, function_body))
