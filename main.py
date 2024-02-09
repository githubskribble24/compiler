import sys
from compiler.compile import main

if __name__ == "__main__":
    if sys.argv[1] == "":
        print("Please give us a .c file to compile")
        sys.exit()
    main(sys.argv[1])
