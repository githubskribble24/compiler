import sys
import os
from typing import List
import platform
import subprocess

from compiler.parser.lexer import NewLexer, LexerError
from compiler.parser.parse import Parser
from compiler.tacky.tackyAST import gen
from compiler.assembly.ASM import createAsmCode, createASMoutput, saveASMToFile
import compiler.semantic_analysis.var_resolution as var_resoltion


def check_setup() -> bool:
    """Make sure the system requirements are met"""

    # A list of issues we can print at the end of the check
    list_issues: List[str] = []

    # Check the Python version
    if sys.version_info.major < 3 or sys.version_info.minor < 8:
        print("Please make sure you use Python 3.8 or above")
        return False

    # Check the operating system and architecture
    machine = platform.machine().lower()
    system = platform.system()

    VALID_ARCHS: List[str] = ["x86_64", "amd64"]
    # this means we are on a Mac
    # MacOS make sure they're running on x86_64; if they're on ARM, notify to use Rosetta
    if system == "Darwin":
        if machine in VALID_ARCHS:
            # We are using the right architecture
            pass

        elif machine == "arm64":
            # we're on an ARM64 machine
            # if Python reports that machine is arm64 but processor is i386,
            # that means we're running under Rosetta2
            # (see https://github.com/python/cpython/issues/96993)
            if platform.processor().lower() != "i386":
                list_issues.append(
                    """You're running macOS on ARM. You need to use Rosetta to emulate x86-64.
Use this command to open an x86-64 shell:
 arch -x86_64 zsh
Then try running this script again from that shell.
"""
                )
        else:
            # We're running some other (very old) architecture, we can't run x86-64 binar
            print(
                f"This architecture isn't supported. (Machine name is {machine}, we need x86_64/AMD64.)"
            )
            return False

    elif machine not in VALID_ARCHS:
        print(
            f"This architecture isn't supported. (Machine name is {machine}, we need x86_64/AMD64)"
        )
        return False

    elif system == "Windows":
        # the architecture is right but they need to use WSL
        print(
            """You're running Windows. You need to use WSL to emulate Linux.
Follow these instructions to install WSL and set up a Linux distribution on your machine: https://learn.microsoft.com/en-us/windows/wsl/install.
Then clone the test suite in your Linux distribution and try this command again from there.
            """
        )
        return False

    elif system not in ["Linux", "FreeBSD"]:
        # This is probably some other Unix-like system; it'll probably work but I haven't tested it
        list_issues.append(
            "This OS isn't officially supported. You might be able to use this compiler on this system, but no guarantees."
        )

    # Check that GCC has been installed and can be used
    try:
        subprocess.run(["gcc", "-v"], check=True, capture_output=True)
    except FileNotFoundError:
        list_issues.append("""Can't find the GCC command, please make sure it is installed and working.
""")

    if list_issues:
        print("\n\n".join(list_issues))
        return False

    return True


def main(file) -> None:
    if not check_setup():
        return
    filePath = file
    sourceFileName = os.path.basename(filePath).split(".")[0]
    assemblyFileName = sourceFileName + ".s"

    with open(filePath) as sourceFile:
        code = sourceFile.read()

    # Start lexer
    try:
        lexerClass = NewLexer(code)
        lexerClass.startLexer()
        Tokens = lexerClass.TOKENS
    except LexerError as err:
        print(f"There was a match not found {err}")
        sys.exit()

    # Start parser
    program = Parser(Tokens)

    # Semantic Analysis
    validated_ast = var_resoltion.resolve(program)

    # Convert AST to TACKY
    TackyProgram = gen(validated_ast)

    # Turn into ASM
    AsmProgram = createAsmCode(TackyProgram)

    # Create ASM code
    AsmCode = createASMoutput(AsmProgram)
    # print(AsmCode)

    # Create assembly file and insert code
    saveASMToFile(AsmCode, f"compiled/{assemblyFileName}")

    # Compile the program
    os.system(f"gcc compiled/{assemblyFileName} -o compiled/{sourceFileName}")

    # All done
    print(f"You can find your binary in ./compiled/{sourceFileName}")
