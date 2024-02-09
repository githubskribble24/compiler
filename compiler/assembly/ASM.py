import sys

import compiler.tacky.tacky_ir as Tacky
from compiler.parser.lexer import TokenType


# instruction
# can be a not or neg operator
class Unary:
    """Unary instruction, can be a Not or Neg operator"""
    def __init__(self, unary_operator, operand):
        # unary_operator = Neg | Not
        self.unary_operator = unary_operator
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.operand = operand


# instruction
class Binary:
    """Binary instruction"""
    def __init__(self, binary_operator, operand1, operand2):
        # unary_operator = Neg | Not
        self.binary_operator = binary_operator
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.operand1 = operand1
        self.operand2 = operand2

    def __str__(self) -> str:
        # TO-DO: replace spaces with "\t", \t does not work here find out why
        return f"{self.binary_operator}     {self.operand1}, {self.operand2}"


#  Cmp(operand, operand)
# instruction
class Cmp:
    """Compare instruction compare the given operands, will set a Status flag after this instruction"""
    def __init__(self, operand1, operand2):
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.operand1 = operand1
        self.operand2 = operand2

    def __str__(self) -> str:
        return f"cmpl\t{self.operand1}, {self.operand2}"


# instruction
class Cdq:
    """Convert word to doubleword or convert doubleword to quadword in the EDX:EAX register"""
    def __str__(self) -> str:
        return "cdq"


# instruction
class Jmp:
    """Just jump instruction does not vary"""
    def __init__(self, identifier):
        # identifier = label AKA text
        self.identifier = identifier

    def __str__(self) -> str:
        return f"jmp\t.L{self.identifier}"


# instruction
class JmpCC:
    """Jump instruction usage can vary depending on the condition"""
    def __init__(self, cond_code, identifier):
        # cond_code = E | NE | G | GE | L | LE
        self.cond_code = cond_code
        # identifier = label AKA text
        self.identifier = identifier

    def __str__(self) -> str:
        return f"j{self.cond_code}\t.L{self.identifier}"


# instruction
class SetCC:
    """Set the destination operand to 0 or 1 depending on the Status Flags"""
    def __init__(self, cond_code, operand):
        # cond_code = E | NE | G | GE | L | LE
        self.cond_code = cond_code
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.operand = operand

    def __str__(self) -> str:
        return f"set{self.cond_code}\t{self.operand}"


class Label:
    """A label used for jumps"""
    def __init__(self, identifier):
        self.identifier = identifier

    def __str__(self) -> str:
        return f".L{self.identifier}:"


# instruction
class Idiv:
    """Instruction that divides value by EAX register"""
    def __init__(self, operand):
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.operand = operand

    def __str__(self) -> str:
        return f"idivl\t{self.operand}"


# binary_operator
class Mult:
    """Multiply operator"""
    def __init__(self) -> None:
        self.val = "imull"

    def __str__(self) -> str:
        return f"{self.val}"


# binary_operator
class Sub:
    """Subtract operator"""
    def __init__(self) -> None:
        self.val = "sub"

    def __str__(self) -> str:
        return f"{self.val}"


# binary_operator
class Add:
    """Add operator"""
    def __init__(self) -> None:
        self.val = "add"

    def __str__(self) -> str:
        return f"{self.val}"


# unary_operator
class Not:
    """Unary Not (~) operator"""
    def __init__(self):
        self.val = "notl"

    def __str__(self):
        return f"{self.val}"


# unary_operator
class Neg:
    """Unary negate (!) operator"""
    def __init__(self):
        self.val = "negl"

    def __str__(self):
        return f"{self.val}"


# instruction
# indicates the number of bytes we substract from the RSP
# subq {int}, %rsp
class AllocateStack:
    """How much to allocate the stack by at the beginning of the program. Indicates the number of bytes we subtract from the RSP"""
    def __init__(self, intval):
        self.int = intval

    def __str__(self):
        # *4 because we use bytes
        return f"-{self.int*4}"


# operand
class Stack:
    """Stack allocation operand"""
    def __init__(self, intval):
        self.int = intval

    def __str__(self) -> str:
        return f"{self.int}(%rbp)"


# operand
class Pseudo:
    """Pseudo operand, used to identify variables"""
    def __init__(self, identifier):
        self.identifier = identifier


# cond_code
# cond_code = E | NE | G | GE | L | LE
class E:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "e"


# cond_code
class NE:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "ne"


# cond_code
class G:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "g"


# cond_code
class GE:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "ge"


# cond_code
class L:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "l"


# cond_code
class LE:
    """Condition code used in SetCC and JmpCC"""
    def __str__(self) -> str:
        return "le"


# operand
# reg = AX | DX | R10 | R11
class Reg:
    """Which register we use"""
    def __init__(self, reg):
        self.reg = reg

    def __str__(self) -> str:
        return f"%{self.reg}"


# operand
class AsmImmediateValue(int):
    """An immediate value like: 5, 6, 7, etc..."""
    def __str__(self) -> str:
        return f"${super().__str__()}"


# instruction
class AsmInstructionRet:
    """Return instruction"""
    def __init__(self):
        self.val = "ret"

    def __str__(self) -> str:
        return "ret"


# instruction
class AsmInstructionMov:
    """Mov instruction"""
    def __init__(self, src, dst):
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.src = src
        # operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
        self.dst = dst

    def __str__(self) -> str:
        return f"movl    {self.src}, {self.dst}"


class AsmFunctionDef:
    """The instruction list for all functions are stored in here"""
    def __init__(self, name, instructionslist):
        self.name = name
        self.instructions = instructionslist


class AsmProgram:
    """The functions are stored in here"""
    def __init__(self, function_definition):
        self.function_definition = function_definition


def createInstructionsList(tackyInstructions):
    ASMInstructions = []
    for instruction in tackyInstructions:
        # This means we have an Unary
        if isinstance(instruction, Tacky.UnaryTacky):

            if isinstance(instruction.unary_operator.operator, Tacky.Not):
                cmpSrc = None
                movDst = None

                if isinstance(instruction.src, Tacky.Constant):
                    cmpSrc = AsmImmediateValue(instruction.src.int)
                elif isinstance(instruction.src, Tacky.Var):
                    cmpSrc = Pseudo(instruction.src.name)

                if isinstance(instruction.dst, Tacky.Constant):
                    movDst = AsmImmediateValue(instruction.dst.int)
                elif isinstance(instruction.dst, Tacky.Var):
                    movDst = Pseudo(instruction.dst.name)

                assert cmpSrc is not None
                assert movDst is not None

                ASMInstructions.append(Cmp(AsmImmediateValue(0), cmpSrc))
                ASMInstructions.append(AsmInstructionMov(AsmImmediateValue(0), movDst))
                ASMInstructions.append(SetCC(E(), movDst))

            else:
                movSrc = None
                movDst = None
                new_unary_operator = None

                if isinstance(instruction.src, Tacky.Constant):
                    movSrc = AsmImmediateValue(instruction.src.int)
                elif isinstance(instruction.src, Tacky.Var):
                    movSrc = Pseudo(instruction.src.name)

                if isinstance(instruction.dst, Tacky.Constant):
                    movDst = AsmImmediateValue(instruction.dst.int)
                elif isinstance(instruction.dst, Tacky.Var):
                    movDst = Pseudo(instruction.dst.name)

                if instruction.unary_operator.operator == TokenType.UNARY_NEGATE:
                    new_unary_operator = Neg()
                elif instruction.unary_operator.operator == TokenType.UNARY_TILDE:
                    new_unary_operator = Not()

                assert movSrc is not None
                assert movDst is not None
                assert new_unary_operator is not None

                ASMInstructions.append(AsmInstructionMov(movSrc, movDst))
                ASMInstructions.append(Unary(new_unary_operator, movDst))

        # This means we have a binary
        elif isinstance(instruction, Tacky.Binary):

            if isinstance(instruction.operator, Tacky.Divide) or isinstance(instruction.operator, Tacky.Remainder):
                dst = None
                register = None
                idiv = None
                src1Mov = None

                if isinstance(instruction.src1, Tacky.Constant):
                    src1Mov = AsmInstructionMov(AsmImmediateValue(instruction.src1.int), Reg("EAX"))
                elif isinstance(instruction.src1, Tacky.Var):
                    src1Mov = AsmInstructionMov(Pseudo(instruction.src1.name), Reg("EAX"))

                if isinstance(instruction.src2, Tacky.Constant):
                    idiv = Idiv(AsmImmediateValue(instruction.src2.int))
                elif isinstance(instruction.src2, Tacky.Var):
                    idiv = Idiv(Pseudo(instruction.src2.name))

                if isinstance(instruction.dst, Tacky.Constant):
                    dst = AsmImmediateValue(instruction.dst.int)
                elif isinstance(instruction.dst, Tacky.Var):
                    dst = Pseudo(instruction.dst.name)

                if isinstance(instruction.operator, Tacky.Divide):
                    register = "EAX"
                elif isinstance(instruction.operator, Tacky.Remainder):
                    register = "EDX"

                assert dst is not None
                assert register is not None
                assert idiv is not None
                assert src1Mov is not None

                ASMInstructions.append(src1Mov)
                ASMInstructions.append(Cdq())
                ASMInstructions.append(idiv)
                ASMInstructions.append(AsmInstructionMov(Reg(register), dst))

                continue

            elif (
                isinstance(instruction.operator, Tacky.Add)
                or isinstance(instruction.operator, Tacky.Subtract)
                or isinstance(instruction.operator, Tacky.Multiply)
            ):

                dst = None
                src1 = None
                src2 = None
                new_operator = None

                if isinstance(instruction.dst, Tacky.Constant):
                    dst = AsmImmediateValue(instruction.dst.int)
                elif isinstance(instruction.dst, Tacky.Var):
                    dst = Pseudo(instruction.dst.name)

                if isinstance(instruction.src1, Tacky.Constant):
                    src1 = AsmImmediateValue(instruction.src1.int)
                elif isinstance(instruction.src1, Tacky.Var):
                    src1 = Pseudo(instruction.src1.name)

                if isinstance(instruction.src2, Tacky.Constant):
                    src2 = AsmImmediateValue(instruction.src2.int)
                elif isinstance(instruction.src2, Tacky.Var):
                    src2 = Pseudo(instruction.src2.name)

                if isinstance(instruction.operator, Tacky.Add):
                    new_operator = Add()
                elif isinstance(instruction.operator, Tacky.Subtract):
                    new_operator = Sub()
                elif isinstance(instruction.operator, Tacky.Multiply):
                    new_operator = Mult()

                assert dst is not None
                assert src1 is not None
                assert src2 is not None
                assert new_operator is not None

                ASMInstructions.append(AsmInstructionMov(src1, dst))
                ASMInstructions.append(Binary(new_operator, src2, dst))

                continue

            # binary_operator = Add | Subtract | Multiply | Divide | Remainder | Equal | NotEqual
            #                   | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual
            elif (
                isinstance(instruction.operator, Tacky.Equal)
                or isinstance(instruction.operator, Tacky.NotEqual)
                or isinstance(instruction.operator, Tacky.LessThan)
                or isinstance(instruction.operator, Tacky.LessOrEqual)
                or isinstance(instruction.operator, Tacky.GreaterThan)
                or isinstance(instruction.operator, Tacky.GreaterOrEqual)
            ):
                cmpSrc1 = None
                cmpSrc2 = None
                dst = None
                relational_operator = None

                if isinstance(instruction.src2, Tacky.Constant):
                    cmpSrc2 = AsmImmediateValue(instruction.src2.int)
                elif isinstance(instruction.src2, Tacky.Var):
                    cmpSrc2 = Pseudo(instruction.src2.name)

                if isinstance(instruction.src1, Tacky.Constant):
                    cmpSrc1 = AsmImmediateValue(instruction.src1.int)
                elif isinstance(instruction.src1, Tacky.Var):
                    cmpSrc1 = Pseudo(instruction.src1.name)

                if isinstance(instruction.dst, Tacky.Constant):
                    dst = AsmImmediateValue(instruction.dst.int)
                elif isinstance(instruction.dst, Tacky.Var):
                    dst = Pseudo(instruction.dst.name)

                # E = Equal, NE = NotEqual, G = Greater Than, GE = GreaterThanEqual, L = Lower than, LE = LowerThanEqual
                if isinstance(instruction.operator, Tacky.Equal):
                    relational_operator = E()
                elif isinstance(instruction.operator, Tacky.NotEqual):
                    relational_operator = NE()
                elif isinstance(instruction.operator, Tacky.LessThan):
                    relational_operator = L()
                elif isinstance(instruction.operator, Tacky.LessOrEqual):
                    relational_operator = LE()
                elif isinstance(instruction.operator, Tacky.GreaterThan):
                    relational_operator = G()
                elif isinstance(instruction.operator, Tacky.GreaterOrEqual):
                    relational_operator = GE()

                assert cmpSrc1 is not None
                assert cmpSrc2 is not None
                assert dst is not None
                assert relational_operator is not None

                ASMInstructions.append(Cmp(cmpSrc2, cmpSrc1))
                ASMInstructions.append(AsmInstructionMov(AsmImmediateValue(0), dst))
                ASMInstructions.append(SetCC(relational_operator, dst))

            else:
                print(f"ERROR: Got an unknown instruction, when creating Assembly AST: {instruction.operator.operator}")
                sys.exit()

        elif isinstance(instruction, Tacky.Jump):
            ASMInstructions.append(Jmp(instruction.target))

        elif isinstance(instruction, Tacky.Label):
            ASMInstructions.append(Label(instruction.identifier))

        elif isinstance(instruction, Tacky.Copy):
            src = None
            dst = None

            if isinstance(instruction.src, Tacky.Constant):
                src = AsmImmediateValue(instruction.src.int)
            elif isinstance(instruction.src, Tacky.Var):
                src = Pseudo(instruction.src.name)

            if isinstance(instruction.dst, Tacky.Constant):
                dst = AsmImmediateValue(instruction.dst.int)
            elif isinstance(instruction.dst, Tacky.Var):
                dst = Pseudo(instruction.dst.name)

            assert src is not None
            assert dst is not None

            ASMInstructions.append(AsmInstructionMov(src, dst))

        elif isinstance(instruction, Tacky.JumpIfZero):
            condition = None

            if isinstance(instruction.condition, Tacky.Constant):
                condition = AsmImmediateValue(instruction.condition.int)
            elif isinstance(instruction.condition, Tacky.Var):
                condition = Pseudo(instruction.condition.name)

            assert condition is not None

            ASMInstructions.append(Cmp(AsmImmediateValue(0), condition))
            ASMInstructions.append(JmpCC(E(), instruction.target))

        elif isinstance(instruction, Tacky.JumpIfNotZero):
            condition = None

            if isinstance(instruction.condition, Tacky.Constant):
                condition = AsmImmediateValue(instruction.condition.int)
            elif isinstance(instruction.condition, Tacky.Var):
                condition = Pseudo(instruction.condition.name)

            assert condition is not None

            ASMInstructions.append(Cmp(AsmImmediateValue(0), condition))
            ASMInstructions.append(JmpCC(NE(), instruction.target))

        # This means we have a return statement
        elif isinstance(instruction, Tacky.Return):
            movSrc = None

            if isinstance(instruction.val, Tacky.Constant):
                movSrc = AsmImmediateValue(instruction.val.int)
            elif isinstance(instruction.val, Tacky.Var):
                movSrc = Pseudo(instruction.val.name)

            assert movSrc is not None

            ASMInstructions.append(AsmInstructionMov(movSrc, Reg("eax")))
            ASMInstructions.append(AsmInstructionRet())

    return ASMInstructions


def pseudoToStack(ASMinstructions):
    pseudoRegisters = {}
    registerCount = 0

    for i, instruction in enumerate(ASMinstructions):
        match instruction:
            case value if isinstance(value, Unary):
                # if the operand is not Pseudo then we should continue
                if not isinstance(instruction.operand, Pseudo):
                    continue

                # check if the stack address is not already in pseudoRegisters
                if instruction.operand.identifier not in pseudoRegisters:
                    stackInstructionCount = (registerCount + 1) * -4
                    registerCount += 1
                    pseudoRegisters[instruction.operand.identifier] = stackInstructionCount
                else:
                    stackInstructionCount = pseudoRegisters[instruction.operand.identifier]

                # DEBUGGING

                ASMinstructions[i].operand = Stack(stackInstructionCount)
            case value if isinstance(value, Binary):
                # if the dst or src is not Pseudo then we should continue
                if not isinstance(instruction.operand1, Pseudo) and not isinstance(instruction.operand2, Pseudo):
                    continue

                stackInstructionCount = (registerCount + 1) * -4

                if isinstance(instruction.operand1, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.operand1.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand1.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand1.identifier]

                    ASMinstructions[i].operand1 = Stack(stackInstructionCount)

                if isinstance(instruction.operand2, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.operand2.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand2.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand2.identifier]

                    ASMinstructions[i].operand2 = Stack(stackInstructionCount)

            case value if isinstance(value, Idiv):
                # if the dst or src is not Pseudo then we should continue
                if not isinstance(instruction.operand, Pseudo):
                    continue

                stackInstructionCount = (registerCount + 1) * -4

                if isinstance(instruction.operand, Pseudo):
                    if instruction.operand.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand.identifier]

                    ASMinstructions[i].operand = Stack(stackInstructionCount)

            case value if isinstance(value, AsmInstructionMov):
                # if the dst or src is not Pseudo then we should continue
                if not isinstance(instruction.src, Pseudo) and not isinstance(instruction.dst, Pseudo):
                    continue

                stackInstructionCount = (registerCount + 1) * -4

                if isinstance(instruction.src, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.src.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.src.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.src.identifier]

                    ASMinstructions[i].src = Stack(stackInstructionCount)

                if isinstance(instruction.dst, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.dst.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.dst.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.dst.identifier]

                    instruction.dst = Stack(stackInstructionCount)

            case value if isinstance(value, Cmp):
                # if the dst or src is not Pseudo then we should continue
                if not isinstance(instruction.operand1, Pseudo) and not isinstance(instruction.operand2, Pseudo):
                    continue

                stackInstructionCount = (registerCount + 1) * -4

                if isinstance(instruction.operand1, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.operand1.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand1.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand1.identifier]

                    ASMinstructions[i].operand1 = Stack(stackInstructionCount)

                if isinstance(instruction.operand2, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.operand2.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand2.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand2.identifier]

                    ASMinstructions[i].operand2 = Stack(stackInstructionCount)

            case value if isinstance(value, SetCC):
                # if the dst or src is not Pseudo then we should continue
                if not isinstance(instruction.operand, Pseudo):
                    continue

                stackInstructionCount = (registerCount + 1) * -4

                if isinstance(instruction.operand, Pseudo):
                    # check if the stack address is not already in pseudoRegisters
                    if instruction.operand.identifier not in pseudoRegisters:
                        stackInstructionCount = (registerCount + 1) * -4
                        registerCount += 1
                        pseudoRegisters[instruction.operand.identifier] = stackInstructionCount
                    else:
                        stackInstructionCount = pseudoRegisters[instruction.operand.identifier]

                    ASMinstructions[i].operand = Stack(stackInstructionCount)

    return ASMinstructions, registerCount


def fixInvalidCmpInstructions(ASMinstructions):
    newInstructions = []
    for instruction in ASMinstructions:
        # instruction is not a Mov instruction, so do nothing
        if not isinstance(instruction, Cmp):
            newInstructions.append(instruction)
            continue

        # there is nothing to fix
        if isinstance(instruction.operand1, Stack) and isinstance(instruction.operand2, Stack):
            newInstructions.append(AsmInstructionMov(instruction.operand1, Reg("r10d")))
            newInstructions.append(Cmp(Reg("r10d"), instruction.operand2))

        elif isinstance(instruction.operand2, AsmImmediateValue):
            newInstructions.append(AsmInstructionMov(instruction.operand2, Reg("r11d")))
            newInstructions.append(Cmp(instruction.operand1, Reg("r11d")))

        else:
            newInstructions.append(instruction)
            continue

    return newInstructions


def fixInvalidIdivInstructions(ASMinstructions):
    newInstructions = []
    for instruction in ASMinstructions:
        # instruction is not a Mov instruction, so do nothing
        if not isinstance(instruction, Idiv):
            newInstructions.append(instruction)
            continue

        # there is nothing to fix
        if not isinstance(instruction.operand, AsmImmediateValue):
            newInstructions.append(instruction)
            continue

        newInstructions.append(AsmInstructionMov(instruction.operand, Reg("r10d")))
        newInstructions.append(Idiv(Reg("r10d")))

    return newInstructions


def fixInvalidBinaryInstructions(ASMinstructions):
    newInstructions = []
    for instruction in ASMinstructions:
        # instruction is not a Mov instruction, so do nothing
        if not isinstance(instruction, Binary):
            newInstructions.append(instruction)
            continue

        # there is nothing to fix
        if not isinstance(instruction.binary_operator, Add) and not isinstance(instruction.binary_operator, Sub) and not isinstance(instruction.binary_operator, Mult):
            newInstructions.append(instruction)
            continue

        if isinstance(instruction.binary_operator, Add) or isinstance(instruction.binary_operator, Sub):
            if not isinstance(instruction.operand1, Stack) and not isinstance(instruction.operand2, Stack):
                newInstructions.append(instruction)
                continue

            newInstructions.append(AsmInstructionMov(instruction.operand1, Reg("r10d")))
            newInstructions.append(Binary(instruction.binary_operator, Reg("r10d"), instruction.operand2))

        elif isinstance(instruction.binary_operator, Mult):
            if not isinstance(instruction.operand2, Stack):
                newInstructions.append(instruction)
                continue

            newInstructions.append(AsmInstructionMov(instruction.operand2, Reg("r11d")))
            newInstructions.append(Binary(instruction.binary_operator, instruction.operand1, Reg("r11d")))
            newInstructions.append(AsmInstructionMov(Reg("r11d"), instruction.operand2))

        else:
            continue

    return newInstructions


def fixInvalidMovInstructions(ASMinstructions):
    newInstructions = []
    for instruction in ASMinstructions:
        # instruction is not a Mov instruction, so do nothing
        if not isinstance(instruction, AsmInstructionMov):
            newInstructions.append(instruction)
            continue

        # there is nothing to fix
        if not isinstance(instruction.src, Stack) and not isinstance(instruction.dst, Stack):
            newInstructions.append(instruction)
            continue

        newInstructions.append(AsmInstructionMov(instruction.src, Reg("r10d")))
        newInstructions.append(AsmInstructionMov(Reg("r10d"), instruction.dst))

    return newInstructions


# TO-DO function from Tacky-AST to ASM
def createAsmCode(normalProgram):
    ASMInstructions = createInstructionsList(normalProgram.function_definition.body)
    ASMInstructions, lastRegisterPosition = pseudoToStack(ASMInstructions)

    if lastRegisterPosition > 0:
        # add AllocateStack at beginning of the instruction
        ASMInstructions.insert(0, AllocateStack(lastRegisterPosition))

    ASMInstructions = fixInvalidMovInstructions(ASMInstructions)
    ASMInstructions = fixInvalidIdivInstructions(ASMInstructions)
    ASMInstructions = fixInvalidBinaryInstructions(ASMInstructions)
    ASMInstructions = fixInvalidCmpInstructions(ASMInstructions)

    # exp = AsmImmediateValue(normalProgram.function_def.body.exp.int)
    # sys.exit()
    # MovInstruction = AsmInstructionMov(exp, "%eax")
    # RetInstruction = AsmInstructionRet()
    function_definition = AsmFunctionDef(normalProgram.function_definition.name, ASMInstructions)
    MyAsmProgram = AsmProgram(function_definition)

    return MyAsmProgram


"""
    ASM CODE GENERATOR
"""


def asmInstructionCodeGenerator(instructions_list, asmOutput):
    """
        instruction = Mov(operand src, operand dst)
        | Unary(unary_operator, operand)
        | AllocateStack(int)
        | Ret
    """
    for instruction in instructions_list:
        if isinstance(instruction, AsmInstructionMov):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, AsmInstructionRet):
            asmOutput = f"""{asmOutput}
    movq    %rbp, %rsp
    popq    %rbp
    ret
"""
            continue

        if isinstance(instruction, Unary):
            asmOutput = f"""{asmOutput}
    {instruction.unary_operator}   {instruction.operand}
"""
            continue

        if isinstance(instruction, AllocateStack):
            asmOutput = f"""{asmOutput}
    subq    ${instruction}, %rsp
"""
            continue

        if isinstance(instruction, Binary):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, Idiv):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, Cdq):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, Cmp):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, Jmp):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, JmpCC):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, SetCC):
            asmOutput = f"""{asmOutput}
    {instruction}
"""
            continue

        if isinstance(instruction, Label):
            asmOutput = f"""{asmOutput}
{instruction}
"""
            continue

    return asmOutput


def asmFunctionCodeGenerator(Function_definition):
    asmOutput = f"""
.globl  {Function_definition.name}
{Function_definition.name}:
    push    %rbp
    movq    %rsp, %rbp
"""
    asmOutput = asmInstructionCodeGenerator(Function_definition.instructions, asmOutput)
    return asmOutput


def createASMoutput(ASMProgram):
    if sys.platform == "darwin":
        ASMProgram.function_definition.name = "_" + ASMProgram.function_definition.name

    asmOutput = asmFunctionCodeGenerator(ASMProgram.function_definition)

    # If on linux type machine we add some assembly code at the end
    # .section .note.GNU-stack,"",@progbits
    if sys.platform == "darwin" or sys.platform == "linux" or sys.platform == "linux2":
        linuxHardening = '\t.section .note.GNU-stack,"",@progbits'
        asmOutput = asmOutput + "\n" + linuxHardening + "\n"

    return asmOutput


def saveASMToFile(code, ASMFileName):
    with open(ASMFileName, "w") as ASMFile:
        ASMFile.write(code)
