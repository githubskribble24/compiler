# C Compiler
The AST definition can be found in AST.md
The formal grammar can be found in grammar.md the grammar in this project is in EBNF notation (more information on EBNF notation here: https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form).

## Requirements
You need to be running on x86_64 or AMD64 architecture. If you are using Windows make sure you are using WSL.

## Setup
```
git clone https://github.com/githubskribble24/compiler.git
```

## Usage Examples
At this moment this compiler is only able to have the main function.
Inside of this function we can only do variable declarations, initialization, assignments, logical operations and math.

If you have the following source file ./file.c
```
int main(void) {
	int b = 5;
	int c = 10;
	return c * b;
}
```
You can compile and run it
```
$ python3 main.py file.c
$ ./compiled/file
$ echo $?
50
```

## TO-DO
- Add Bitiwse Operators (&, |, ^, <<, >>)
