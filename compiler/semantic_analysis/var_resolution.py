import sys

from compiler.parser.AST import (
    Declaration,
    ReturnStatement,
    Null,
    Assignment,
    Binary,
    Var,
    Unary,
    Constant,
    Program,
    FunctionDefinition,
)


class Semantic_Analysis:

    def __init__(self) -> None:
        pass


def make_uniquename(name, variable_map: dict):
    next_variablecount = len(variable_map)

    newname = f"{str(name)}.{next_variablecount}"

    return newname


def resolve_exp(exp, variable_map: dict):
    if isinstance(exp, Assignment):
        if not isinstance(exp.left_exp, Var):
            print("Invalid lvalue!")
            sys.exit()
        return Assignment(resolve_exp(exp.left_exp, variable_map), resolve_exp(exp.right_exp, variable_map))
    elif isinstance(exp, Var):
        if exp.identifier in variable_map:
            return Var(variable_map[exp.identifier])
        else:
            print("Undeclared variable!")
            sys.exit()
    elif isinstance(exp, Unary):
        return Unary(exp.unary_operator, resolve_exp(exp.exp, variable_map))
    elif isinstance(exp, Binary):
        return Binary(exp.binary_operator, resolve_exp(exp.exp1, variable_map), resolve_exp(exp.exp2, variable_map))
    elif isinstance(exp, Constant):
        return Constant(exp.int)
    else:
        print(exp)
        print("Trying to resolve an unknown expression!")
        sys.exit()


def resolve_statement(statement: ReturnStatement | Null | Assignment | Binary | Constant | Var | Unary, variable_map: dict):
    if isinstance(statement, ReturnStatement):
        return ReturnStatement(resolve_exp(statement.exp, variable_map))
    elif isinstance(statement, (Assignment, Binary, Constant, Var, Unary)):
        return resolve_exp(statement, variable_map)
    elif isinstance(statement, Null):
        return Null()
    else:
        print("Gotten wrong statement")
        sys.exit()


def resolve_declaration(declaration: Declaration, variable_map: dict):
    if declaration.name in variable_map:
        print("Duplicate variable declaraiont")
        sys.exit()

    unique_name = make_uniquename(declaration.name, variable_map)
    variable_map[declaration.name] = unique_name

    if declaration.init is not None:
        declaration.init = resolve_exp(declaration.init, variable_map)

    declaration.name = unique_name

    return [declaration, variable_map]


def resolve_function_def(function_def: FunctionDefinition):
    variable_map = {}
    body = []

    for line in function_def.body:
        if isinstance(line, (ReturnStatement, Null, Assignment, Binary, Constant, Var, Unary)):
            new_body = resolve_statement(line, variable_map)
            body.append(new_body)
        elif isinstance(line, Declaration):
            new_body, variable_map = resolve_declaration(line, variable_map)
            body.append(new_body)
        else:
            print(line)
            print("Gotten wrong function definition body wtf")
            sys.exit()

    return FunctionDefinition(function_def.name, body)


# TO-DO: make a seperate function to go through the block-items
#        this is needed because variable scopes are different in other functions


def resolve(program: Program):
    return Program(resolve_function_def(program.function_def))
