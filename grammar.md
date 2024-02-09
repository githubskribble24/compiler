<program> ::= <function> 
<function> ::= "int" <identifier> "(" "void" ")" "{" { <block-item> } "}"

<block-item> ::= <statement> | <declaration>
<declaration> ::= "int" <identifier> [ "=" exp ] ";"
<statement> ::= "return" <exp> ";" | <exp> ";" | ";"

<exp> ::= <factor> | <exp> <binop> <exp>
<factor> ::= <int> | <identifier> | <unary_op> <factor> | "(" <exp> ")"
<unary_op> ::= "~" | "-" | "!"
<binop> ::= "+" | "-" | "*" | "/" | "%" | "&&" | "||" | "==" | "!=" | "<" | "<=" | ">" | ">=" | "="
<identifier> ::= ? An identifier token ?
<int> ::= ? A constant token ?