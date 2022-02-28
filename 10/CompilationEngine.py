"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer

NEWLINE, PERIOD, OPEN_PAREN, CLOSE_PAREN, OPEN_SQUARE, CLOSE_SQUARE, \
    OPEN_CB, CLOSE_CB, COMMA, SEMICOLON, EQUALS = \
    '\n', '.', '(', ')', '[', ']', '{', '}', ',', ';', '='

KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST, CLASS, \
    CLASS_VAR_DEC, SUBROUTINE_DEC, PARAMETER_LIST, SUBROUTINE_BODY, VAR_DEC, \
    STATEMENTS, LET_STATEMENT, IF_STATEMENT, WHILE_STATEMENT, DO_STATEMENT, \
    RETURN_STATEMENT, EXPRESSION, TERM, EXPRESSION_LIST, OP, UNARY_OP, \
    KEYWORD_CONSTANT = range(23)

LET, IF, WHILE, DO, RETURN = "let", "if", "while", "do", "return"

SYNTAX_ERR, INT_ERR = "SyntaxError: Invalid syntax in Jack code.\n", \
                      "IntegerError: Integer is out of range.\n"

tags = {KEYWORD: "keyword", SYMBOL: "symbol", IDENTIFIER: "identifier",
        INT_CONST: "integerConstant", STRING_CONST: "stringConstant",
        CLASS: "class", CLASS_VAR_DEC: "classVarDec",
        SUBROUTINE_DEC: "subroutineDec", PARAMETER_LIST: "parameterList",
        SUBROUTINE_BODY: "subroutineBody", VAR_DEC: "varDec",
        STATEMENTS: "statements", LET_STATEMENT: "letStatement",
        IF_STATEMENT: "ifStatement", WHILE_STATEMENT: "whileStatement",
        DO_STATEMENT: "doStatement", RETURN_STATEMENT: "returnStatement",
        EXPRESSION: "expression", TERM: "term",
        EXPRESSION_LIST: "expressionList", OP: "op", UNARY_OP: "unaryOp",
        KEYWORD_CONSTANT: "keywordConstant"}

atoms = {KEYWORD: "KEYWORD", SYMBOL: "SYMBOL", IDENTIFIER: "IDENTIFIER",
         INT_CONST: "INT_CONST", STRING_CONST: "STRING_CONST"}

statement_keywords = {LET, IF, WHILE, DO, RETURN}
ops = {'+', '-', '*', '/', '&', '|', '<', '>', '='}
special_ops = {'<': "&lt;", '>': "&gt;", '"': "&quot;", '&': "&amp;"}
unary_ops = {'-', '~', '^', "#"}
keyword_constants = {"true", "false", "null", "this"}


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: typing.TextIO,
                 output_stream: typing.TextIO) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.tokenizer = JackTokenizer(input_stream)
        self.output_stream = output_stream

        self.tokenizer.advance()

    def __get_cur_token(self) -> str or int:
        """
        Gets the current token.
        :return: The current token.
        """
        token_type = self.tokenizer.token_type()

        if token_type == atoms[KEYWORD]:
            return self.tokenizer.keyword().lower()
        elif token_type == atoms[SYMBOL]:
            return self.tokenizer.symbol()
        elif token_type == atoms[IDENTIFIER]:
            return self.tokenizer.identifier()
        elif token_type == atoms[INT_CONST]:
            return self.tokenizer.int_val()
        elif token_type == atoms[STRING_CONST]:
            return self.tokenizer.string_val()

    def __validate(self, elem_type, valid_options=None) -> None:
        """
        Validates token according to expected Jack semantics.
        :param elem_type: The type of element expected.
        :param valid_options (optional): A set of possible next tokens
                                        (single char/string or set).
        """
        # Check that the token type is as expected
        if self.tokenizer.token_type() != atoms[elem_type]:
            raise Exception(SYNTAX_ERR)
        # Check integer is in range
        if self.tokenizer.token_type() == atoms[INT_CONST]:
            if self.__get_cur_token() < 0 or self.__get_cur_token() > 32767:
                raise Exception(INT_ERR)

        # Compare with valid next keywords, if there are any
        if valid_options:
            cur_token = self.__get_cur_token()
            if cur_token not in valid_options:
                raise Exception(SYNTAX_ERR)

    def __open(self, tag_code, newline=NEWLINE) -> None:
        """
        Writes opening tag to output file.
        :param tag_code: Code as per tags dict.
        :param newline: Trailing newline character to end of opening tag (
                        only nullify for terminal elements).
        """
        self.__write_to_output("<{}> ".format(tags[tag_code]) + newline)

    def __close(self, tag_code):
        """
        Writes closing tag to output file.
        :param tag_code: Code as per tags dict.
        """
        self.__write_to_output(" </{}>".format(tags[tag_code]) + NEWLINE)

    def __write_to_output(self, text) -> None:
        """
        Writes text to output file.
        :param text: Text to write to output file.
        """
        # Replace special chars (as per .xml requirements)
        if text in special_ops:
            text = special_ops[text]

        self.output_stream.write(str(text))

    def __compile_atom(self, elem_type: int, valid_options=None) -> None:
        """
        Compiles an atom i.e. a keyword, symbol, identifier, string
        constant or integer constant.
        :param elem_type: The type of atom.
        :param valid_options (optional): A set of possible next tokens
                                        (single char/string or set).
        """
        # Validate expected semantics
        self.__validate(elem_type, valid_options)
        # Write open label
        self.__open(elem_type, '')
        # Write token
        self.__write_to_output(self.__get_cur_token())
        # Write close label
        self.__close(elem_type)
        # Advance
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def __is_var_dec(self) -> bool:
        """
        Is the next rule a varDec?
        :return: True if next rule is a varDec, else False
        """
        return self.__get_cur_token() == "static" or \
               self.__get_cur_token() == "field"

    def __is_subroutine(self) -> bool:
        """
        Is the next rule a subroutineDec?
        :return: True if next rule is a subroutineDec, else False
        """
        return self.__get_cur_token() == "constructor" or \
               self.__get_cur_token() == "function" or \
               self.__get_cur_token() == "method"

    def __compile_type(self) -> None:
        """
        Compiles type Rule.

        'int'|'char|'boolean|className
        """
        token_type = self.tokenizer.token_type()

        if token_type == atoms[KEYWORD]:
            self.__compile_atom(KEYWORD, {"int", "char", "boolean"})
        elif token_type == atoms[IDENTIFIER]:
            self.__compile_atom(IDENTIFIER)  # className
        else:
            raise Exception(SYNTAX_ERR)

    def __compile_void_or_type(self) -> None:
        """
        Compiles keyword 'void' or a type.

        'void'|type
        """
        token_type = self.tokenizer.token_type()

        if self.__get_cur_token() == "void":
            self.__compile_atom(KEYWORD, {"void"})
        else:
            self.__compile_type()

    def __compile_subroutine_body(self) -> None:
        """
        Compiles subroutineBody Rule.

        '{' varDec* statements '}'
        """
        self.__open(SUBROUTINE_BODY)

        self.__compile_atom(SYMBOL, OPEN_CB)  # '{'

        while self.__get_cur_token() == "var":
            self.compile_var_dec()  # varDec

        self.compile_statements()  # statements
        self.__compile_atom(SYMBOL, CLOSE_CB)  # '}'

        self.__close(SUBROUTINE_BODY)

    def __compile_subroutine_call(self, from_do=False) -> None:
        """
        Compiles subroutineCall Rule.

        subroutineName '(' expressionList ')' |
        (className|varName) '.' subroutineName '(' expressionList ')'

        :param from_do: Has the method been called from compile_do?
        """
        # If not from_do, then we've arrived after parsing an LL2
        # statement, and the identifier has already been processed.
        if from_do:
            self.__compile_atom(IDENTIFIER)  # subroutineName

        if self.__get_cur_token() == PERIOD:
            self.__compile_atom(SYMBOL, PERIOD)  # '.'
            self.__compile_atom(IDENTIFIER)  # subroutineName

        self.__compile_atom(SYMBOL, OPEN_PAREN)  # '('
        self.compile_expression_list()  # expressionList
        self.__compile_atom(SYMBOL, CLOSE_PAREN)  # ')'

    def __compile_multiple_var_names(self) -> None:
        """
        Compiles multiple varNames sequence.

        type varName (',' varName)* ';'
        """
        self.__compile_type()  # type
        self.__compile_atom(IDENTIFIER)  # varName

        while self.__get_cur_token() == COMMA:
            self.__compile_atom(SYMBOL, COMMA)  # ','
            self.__compile_atom(IDENTIFIER)  # varName

        self.__compile_atom(SYMBOL, SEMICOLON)  # ';'

    def compile_class(self) -> None:
        """Compiles a complete class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.__open(CLASS)

        self.__compile_atom(KEYWORD, {"class"})  # 'class;
        self.__compile_atom(IDENTIFIER)  # className
        self.__compile_atom(SYMBOL, OPEN_CB)  # '{'

        while self.__is_var_dec():
            self.compile_class_var_dec()  # classVarDec

        while self.__is_subroutine():
            self.compile_subroutine()  # subroutineDec

        self.__compile_atom(SYMBOL, CLOSE_CB)  # '}'

        self.__close(CLASS)

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.

        ('static'|'field') type varName (',' varName)* ';'

        """
        self.__open(CLASS_VAR_DEC)

        self.__compile_atom(KEYWORD, {"static", "field"})
        self.__compile_multiple_var_names()  # type varName (',' varName)* ';'

        self.__close(CLASS_VAR_DEC)

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList '); subroutineBody

        """
        self.__open(SUBROUTINE_DEC)

        self.__compile_atom(KEYWORD, {"constructor", "function", "method"})
        self.__compile_void_or_type()  # ('void'|type)
        self.__compile_atom(IDENTIFIER)  # subroutineName
        self.__compile_atom(SYMBOL, OPEN_PAREN)  # '('
        self.compile_parameter_list()  # parameterList
        self.__compile_atom(SYMBOL, CLOSE_PAREN)  # ')'
        self.__compile_subroutine_body()  # subroutineBody

        self.__close(SUBROUTINE_DEC)

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".

        ((type varName) (',' type varName)*)?
        """
        self.__open(PARAMETER_LIST)
        # Note: parameterList only within context of subroutineDec,
        # this cond allows to determine whether List is empty
        if self.__get_cur_token() != CLOSE_PAREN:
            self.__compile_type()  # type
            self.__compile_atom(IDENTIFIER)  # varName

            while self.__get_cur_token() == COMMA:
                self.__compile_atom(SYMBOL, COMMA)  # ','
                self.__compile_type()  # type
                self.__compile_atom(IDENTIFIER)  # varName

        self.__close(PARAMETER_LIST)

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.

        'var' type varName (',' varName)* ';'
        """
        self.__open(VAR_DEC)

        self.__compile_atom(KEYWORD, {"var"})  # 'var'
        self.__compile_multiple_var_names()  # type varName (',' varName)* ';'

        self.__close(VAR_DEC)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".

        statement*
        """
        self.__open(STATEMENTS)

        cur_token = self.__get_cur_token()
        while cur_token in statement_keywords:
            if cur_token == LET:
                self.compile_let()
            elif cur_token == IF:
                self.compile_if()
            elif cur_token == WHILE:
                self.compile_while()
            elif cur_token == DO:
                self.compile_do()
            elif cur_token == RETURN:
                self.compile_return()

            cur_token = self.__get_cur_token()

        self.__close(STATEMENTS)

    def compile_do(self) -> None:
        """Compiles a do statement.

        'do' subroutineCall ';'
        """
        self.__open(DO_STATEMENT)

        self.__compile_atom(KEYWORD, {"do"})  # 'do'
        self.__compile_subroutine_call(from_do=True)  # subroutineCall
        self.__compile_atom(SYMBOL, SEMICOLON)  # ';'

        self.__close(DO_STATEMENT)

    def compile_let(self) -> None:
        """Compiles a let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.__open(LET_STATEMENT)

        self.__compile_atom(KEYWORD, {"let"})  # 'let'
        self.__compile_atom(IDENTIFIER)  # varName

        if self.__get_cur_token() == OPEN_SQUARE:
            self.__compile_atom(SYMBOL, OPEN_SQUARE)  # '['
            self.compile_expression()  # expression
            self.__compile_atom(SYMBOL, CLOSE_SQUARE)  # '['

        self.__compile_atom(SYMBOL, EQUALS)  # '='
        self.compile_expression()  # expression
        self.__compile_atom(SYMBOL, SEMICOLON)  # ';'

        self.__close(LET_STATEMENT)

    def compile_while(self) -> None:
        """Compiles a while statement.

        'while' '(' expression ')' '{' statements '}'
        """
        self.__open(WHILE_STATEMENT)

        self.__compile_atom(KEYWORD, {"while"})  # 'while'

        self.__compile_atom(SYMBOL, OPEN_PAREN)  # '('
        self.compile_expression()  # expression
        self.__compile_atom(SYMBOL, CLOSE_PAREN)  # ')'

        self.__compile_atom(SYMBOL, OPEN_CB)  # '{'
        self.compile_statements()  # expression
        self.__compile_atom(SYMBOL, CLOSE_CB)  # '}'

        self.__close(WHILE_STATEMENT)

    def compile_return(self) -> None:
        """Compiles a return statement.

        'return' expression? ';'
        """
        self.__open(RETURN_STATEMENT)

        self.__compile_atom(KEYWORD, {"return"})  # 'return'

        if self.__get_cur_token() != SEMICOLON:
            self.compile_expression()  # expression

        self.__compile_atom(SYMBOL, SEMICOLON)  # ';'

        self.__close(RETURN_STATEMENT)

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause.

        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        """
        self.__open(IF_STATEMENT)

        self.__compile_atom(KEYWORD, {"if"})  # 'if'

        self.__compile_atom(SYMBOL, OPEN_PAREN)  # '('
        self.compile_expression()  # expression
        self.__compile_atom(SYMBOL, CLOSE_PAREN)  # ')'

        self.__compile_atom(SYMBOL, OPEN_CB)  # '{'
        self.compile_statements()  # statements
        self.__compile_atom(SYMBOL, CLOSE_CB)  # '}'

        if self.__get_cur_token() == "else":
            self.__compile_atom(KEYWORD, {"else"})  # 'else'

            self.__compile_atom(SYMBOL, OPEN_CB)  # '{'
            self.compile_statements()  # statements
            self.__compile_atom(SYMBOL, CLOSE_CB)  # '}'

        self.__close(IF_STATEMENT)

    def compile_expression(self) -> None:
        """Compiles an expression.

        term (op term)*
        """
        self.__open(EXPRESSION)

        self.compile_term()  # term

        while self.__get_cur_token() in ops:
            self.__compile_atom(SYMBOL, ops)  # op
            self.compile_term()  # term

        self.__close(EXPRESSION)

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "."
        suffices to distinguish between the three possibilities. Any other
        token is not part of this term and should not be advanced over.

        integerConstant|stringConstant|keywordConstant|varName| /
        varName'[' expression ']'|subroutineCall|'(' expression ')'|unaryOp /
        term

        """
        self.__open(TERM)

        token_type = self.tokenizer.token_type()

        # Handle case of LL2 specified in docstring
        if token_type == atoms[IDENTIFIER]:
            self.__compile_atom(IDENTIFIER)
            # Array entry
            if self.__get_cur_token() == OPEN_SQUARE:
                self.__compile_atom(SYMBOL, OPEN_SQUARE)
                self.compile_expression()
                self.__compile_atom(SYMBOL, CLOSE_SQUARE)
            # subroutineCall
            elif self.__get_cur_token() == PERIOD or \
                    self.__get_cur_token() == OPEN_PAREN:
                self.__compile_subroutine_call()
            # Regular varName
            else:
                pass

        elif token_type == atoms[INT_CONST]:
            self.__compile_atom(INT_CONST)
        elif token_type == atoms[STRING_CONST]:
            self.__compile_atom(STRING_CONST)
        elif token_type == atoms[KEYWORD]:
            self.__compile_atom(KEYWORD, keyword_constants)
        elif self.__get_cur_token() == OPEN_PAREN:
            self.__compile_atom(SYMBOL, OPEN_PAREN)
            self.compile_expression()
            self.__compile_atom(SYMBOL, CLOSE_PAREN)
        elif token_type == atoms[SYMBOL]:
            self.__compile_atom(SYMBOL, unary_ops)
            self.compile_term()

        self.__close(TERM)

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions.

        (expression (',' expression)* )?
        """
        self.__open(EXPRESSION_LIST)

        # Note: parameterList only withing context of subroutineDec,
        # this mechanism allows to determine whether List is empty
        if self.__get_cur_token() != CLOSE_PAREN:
            self.compile_expression()  # expression

            while self.__get_cur_token() == COMMA:
                self.__compile_atom(SYMBOL, COMMA)  # ','
                self.compile_expression()  # expression

        self.__close(EXPRESSION_LIST)
