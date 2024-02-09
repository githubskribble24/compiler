import sys

import compiler.parser.AST as AST
import compiler.tacky.tacky_ir as Tacky
from compiler.parser.lexer import TokenType

# this is here to keep count of the temporary names made
namecount = 0
uniquenamecount = 0

"""
        THE TACKY IR
program = Program(function_definition)
function_definition = Function(identifier, instruction* body)
instruction = Return(val)
                | Unary(unary_operator, val src, val dst)
                | Binary(binary_operator, val src1, val src2, val dst)
                | Copy(val src, val dst)
                | Jump(identifier target)
                | JumpIfZero(val condition, identifier target)
                | JumpIfNotZero(val condition, identifier target)
                | Label(identifier)
val = Constant(int) | Var(identifier)
unary_operator = Complement | Negate | Not
binary_operator = Add | Subtract | Multiply | Divide | Remainder | Equal
                    | NotEqual | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual
"""


# ASDL for Tacky
def make_temporaryname():
    global namecount

    newname = f"tmp{namecount}"
    namecount += 1

    return newname


def make_uniquename(name):
    global uniquenamecount

    newname = f"{str(name)}{uniquenamecount}"
    uniquenamecount += 1

    return newname


def convert_unop(op):
    if op.operator == TokenType.UNARY_NEGATE:
        temp_tacky = Tacky.Tacky_Unary_Operator(op.operator)
    elif op.operator == TokenType.UNARY_TILDE:
        temp_tacky = Tacky.Tacky_Unary_Operator(op.operator)
    elif op.operator == TokenType.NOT_OPERATOR:
        temp_tacky = Tacky.Tacky_Unary_Operator(Tacky.Not())
    else:
        print(f"Something went wrong when converting the unary operator to tacky, got operator: {op.operator}, Expect: UNARY_NEGATE or UNARY_TILDE")
        sys.exit()
    return temp_tacky


def convert_binop(binary_operator):
    if binary_operator.operator not in AST.Binary_Operator.operatorsList:
        print(f"Something went wrong when converting the binary operator to tacky, got operator: {binary_operator.operator}, Expected a Binary Operator ")
        sys.exit()

    new_operator = None

    match binary_operator.operator:
        case TokenType.PLUS_OPERATOR:
            new_operator = Tacky.Add()
        case TokenType.MULTIPLICATION_OPERATOR:
            new_operator = Tacky.Multiply()
        case TokenType.DIVISION_OPERATOR:
            new_operator = Tacky.Divide()
        case TokenType.REMAINDER_OPERATOR:
            new_operator = Tacky.Remainder()
        case TokenType.UNARY_NEGATE:
            new_operator = Tacky.Subtract()
        case TokenType.EQ_OPERATOR:
            new_operator = Tacky.Equal()
        case TokenType.NEQ_OPERATOR:
            new_operator = Tacky.NotEqual()
        case TokenType.LTE_OPERATOR:
            new_operator = Tacky.LessOrEqual()
        case TokenType.LT_OPERATOR:
            new_operator = Tacky.LessThan()
        case TokenType.GTE_OPERATOR:
            new_operator = Tacky.GreaterOrEqual()
        case TokenType.GT_OPERATOR:
            new_operator = Tacky.GreaterThan()
        case (TokenType.AND_OPERATOR | TokenType.OR_OPERATOR):
            print("Internal error, cannot convert these (and/or) operator directly to TACKY binops")
            sys.exit()
        case _:
            print(binary_operator.operator)
            print("Internal error, no binary operation has been found")
            sys.exit()

    assert new_operator is not None

    return new_operator


def emit_unary_expression(operator):
    eval_inner, src = emit_tacky(operator.exp)

    # Create a temporary variable name to use in the assembly
    dst_name = make_temporaryname()

    # Turn the dst name into a variable
    dst = Tacky.Var(dst_name)

    # Convert unary operator to it's TACKY equivalent (UnaryTacky)
    tacky_op = convert_unop(operator.unary_operator)

    # Create the instructions list
    eval_inner.append(Tacky.UnaryTacky(tacky_op, src, dst))

    instructions = eval_inner
    return [instructions, dst]


def emit_binary_expression(operator):
    instructions = []

    if operator.binary_operator.operator == TokenType.AND_OPERATOR:
        eval_v1 = None
        eval_v2 = None

        eval_v1, v1 = emit_tacky(operator.exp1)
        eval_v2, v2 = emit_tacky(operator.exp2)

        false_label = make_uniquename("and_false")
        end_label = make_uniquename("and_end")

        dst_name = make_temporaryname()
        dst = Tacky.Var(dst_name)

        assert eval_v1 is not None
        assert eval_v2 is not None

        instructions.extend(eval_v1)
        instructions.append(Tacky.JumpIfZero(v1, false_label))
        instructions.extend(eval_v2)
        instructions.append(Tacky.JumpIfZero(v2, false_label))
        instructions.append(Tacky.Copy(Tacky.Constant(1), dst))
        instructions.append(Tacky.Jump(end_label))
        instructions.append(Tacky.Label(false_label))
        instructions.append(Tacky.Copy(Tacky.Constant(0), dst))
        instructions.append(Tacky.Label(end_label))

        return [instructions, dst]

    elif operator.binary_operator.operator == TokenType.OR_OPERATOR:
        eval_v1 = None
        eval_v2 = None

        eval_v1, v1 = emit_tacky(operator.exp1)
        eval_v2, v2 = emit_tacky(operator.exp2)

        true_label = make_uniquename("or_true")
        end_label = make_uniquename("or_end")

        dst_name = make_temporaryname()
        dst = Tacky.Var(dst_name)

        assert eval_v1 is not None
        assert eval_v2 is not None

        instructions.extend(eval_v1)
        instructions.append(Tacky.JumpIfNotZero(v1, true_label))
        instructions.extend(eval_v2)
        instructions.append(Tacky.JumpIfNotZero(v2, true_label))
        instructions.append(Tacky.Copy(Tacky.Constant(0), dst))
        instructions.append(Tacky.Jump(end_label))
        instructions.append(Tacky.Label(true_label))
        instructions.append(Tacky.Copy(Tacky.Constant(1), dst))
        instructions.append(Tacky.Label(end_label))

        return [instructions, dst]

    else:
        eval_v1 = None
        eval_v2 = None

        eval_v1, v1 = emit_tacky(operator.exp1)
        eval_v2, v2 = emit_tacky(operator.exp2)

        assert eval_v1 is not None
        assert eval_v2 is not None

        dst_name = make_temporaryname()
        dst = Tacky.Var(dst_name)
        tacky_op = convert_binop(operator.binary_operator)

        instructions.extend(eval_v1)
        instructions.extend(eval_v2)
        instructions.append(Tacky.Binary(tacky_op, v1, v2, dst))

        return [instructions, dst]


# Turn AST into TACKY
def emit_tacky_return_statement(exp, instructions=None):
    if instructions is None:
        instructions = []

    if isinstance(exp, AST.Constant):
        return [[], Tacky.Constant(exp.int)]

    elif isinstance(exp, AST.Unary):
        # what it returns: return [instructions, dst]
        return emit_unary_expression(exp)

    elif isinstance(exp, AST.Binary):
        return emit_binary_expression(exp)

    elif isinstance(exp, AST.Var):
        instructions.append(Tacky.Var(exp.identifier))
        return instructions

    elif isinstance(exp, AST.Assignment):
        eval_exp, result = emit_tacky(exp.right_exp)
        instructions.append(Tacky.Copy(result, Tacky.Var(exp.left_exp.identifier)))
        instructions.append(Tacky.Var(exp.left_exp.identifier))
        return instructions

    return None, None


def emit_tacky(exp, instructions=None):
    if instructions is None:
        instructions = []

    if isinstance(exp, AST.Constant):
        return [[], Tacky.Constant(exp.int)]

    elif isinstance(exp, AST.Unary):
        # what it returns: return [instructions, dst]
        return emit_unary_expression(exp)

    elif isinstance(exp, AST.Binary):
        return emit_binary_expression(exp)

    elif isinstance(exp, AST.Var):
        return [[], Tacky.Var(exp.identifier)]

    elif isinstance(exp, AST.Assignment):
        instruct, result = emit_tacky(exp.right_exp)
        if instruct:
            instructions.extend(instruct)
        instructions.append(Tacky.Copy(result, Tacky.Var(exp.left_exp.identifier)))
        return [instructions, Tacky.Var(exp.left_exp.identifier)]

    return None, None


def emit_tacky_for_statement(statement: AST.ReturnStatement | AST.Null | AST.Assignment | AST.Binary | AST.Constant | AST.Var | AST.Unary):
    if not isinstance(statement, (AST.ReturnStatement, AST.Null, AST.Assignment, AST.Binary, AST.Constant, AST.Var, AST.Unary)):
        # this should not happen
        print("Something went wrong, code: #55")
        sys.exit()

    if isinstance(statement, AST.ReturnStatement):
        eval_exp, dst = emit_tacky(statement.exp)

        if eval_exp is None and dst is None:
            print("Something went wrong at Tacky generator")
            sys.exit()

        assert eval_exp is not None

        eval_exp.append(Tacky.Return(dst))

        return [eval_exp, []]
    elif isinstance(statement, AST.Assignment):
        eval_assignment, _assing_result = emit_tacky(statement)
        return [eval_assignment, _assing_result]
    elif isinstance(statement, (AST.Binary, AST.Constant, AST.Var, AST.Unary)):
        eval_assignment, _assing_result = emit_tacky(statement)
        return [eval_assignment, _assing_result]
    else:
        print("Something went wrong when generating tacky for a statement. Unknown statement.")
        sys.exit()


def emit_tacky_for_function(fn_def):
    function_name = fn_def.name
    function_body = fn_def.body
    instructions = []

    for block_item in function_body:
        if isinstance(block_item, (AST.ReturnStatement, AST.Null, AST.Assignment, AST.Binary, AST.Constant, AST.Var, AST.Unary)):
            if isinstance(block_item, AST.Null):
                continue
            eval_result, passing_result = emit_tacky_for_statement(block_item)
            if eval_result:
                instructions.extend(eval_result)
            instructions.append(passing_result)
        elif isinstance(block_item, AST.Declaration):
            if block_item.init is None:
                continue

            eval_assignment, _assing_result = emit_tacky(AST.Assignment(AST.Var(block_item.name), block_item.init))

            if isinstance(eval_assignment, list):
                instructions.extend(eval_assignment)
            else:
                instructions.append(eval_assignment)

    # extra return instruction to make sure we always return something in int main
    instructions.append(Tacky.Return(Tacky.Constant(0)))
    return Tacky.function_Def(function_name, instructions)


def gen(Program):
    return Tacky.Program(emit_tacky_for_function(Program.function_def))
