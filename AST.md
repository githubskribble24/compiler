program = Program(function_definition)
function_definition = Function(identifier name, block_item* body)

block_item = S(statement) | D(decleration)
declaration = Declaration(identifier name, exp? init)
statement = Return(exp) | Expression(exp) | Null

exp = Constant(int)
		 | Var(identifier)
		 | Unary(unary_operator, exp)
		 | Binary(binary_operator, exp, exp)
		 | Assignment(exp, exp)
		 
unary_operator = Complement | Negate
binary_operator = Add | Subtract | Multiply | Divide | Remainder | And | Or | Equal | NotEqual | LessThan | LessOrEqual | GreaterThan | GreaterOrEqual