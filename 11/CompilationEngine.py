"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

L1, L2 = "L1", "L2"

NEWLINE, PERIOD, OPEN_PAREN, CLOSE_PAREN, OPEN_SQUARE, CLOSE_SQUARE, \
    OPEN_CB, CLOSE_CB, COMMA, SEMICOLON, EQUALS = \
    '\n', '.', '(', ')', '[', ']', '{', '}', ',', ';', '='

STATIC, FIELD, CONST, ARG, LOCAL, THIS, THAT, POINTER, TEMP, VAR = \
    "STATIC", "FIELD", "CONST", "ARG", "LOCAL", "THIS", "THAT", "POINTER", \
    "TEMP", "VAR"

ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT, SHIFTLEFT, SHIFTRIGHT = \
    "ADD", "SUB", "NEG", "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", \
    "SHIFTRIGHT"

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
ops = {'+': "ADD", '-': "SUB", '*': "", '/': "", '&': "AND", '|': "OR",
       '<': "LT", '>': "GT", '=': "EQ"}
special_ops = {'<': "&lt;", '>': "&gt;", '"': "&quot;", '&': "&amp;"}
keyword_constants = {"true", "false", "null", "this"}
unary_ops = {'-': "NEG", '~': "NOT", '^': "SHIFTLEFT", "#": "SHIFTRIGHT"}
segments = {"STATIC": "STATIC", "FIELD": "THIS", "ARG": "ARG", "VAR": "LOCAL"}


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
        self.vm_writer = VMWriter(output_stream)
        self.table = SymbolTable()
        self.cur_class = ""

        self.if_counter = 0
        self.while_counter = 0

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

    def __compile_subroutine_call(self, name=None) -> None:
        """
        Compiles subroutineCall Rule.

        subroutineName '(' expressionList ')' |
        (className|varName) '.' subroutineName '(' expressionList ')'
        """
        num_of_args = 0

        if name is None:
            name = self.__get_cur_token()
            # className|varName or subroutineName
            self.tokenizer.advance()

        if self.__get_cur_token() == PERIOD:
            self.tokenizer.advance()  # '.'
            if self.table.contains(name):
                type, kind, index = self.__lookup_table(name)
                self.vm_writer.write_push(segments[kind],
                                          index)  # pushes 'this' to stack
                num_of_args += 1
                name = type + PERIOD + self.__get_cur_token()
                # subroutineName
            else:
                name += PERIOD + self.__get_cur_token()
            self.tokenizer.advance()
        else:
            self.vm_writer.write_push(POINTER, 0)
            num_of_args += 1
            name = self.cur_class + PERIOD + name

        self.tokenizer.advance()  # '('
        num_of_args += self.compile_expression_list()  # expressionList
        self.vm_writer.write_call(name, num_of_args)
        self.tokenizer.advance()  # ')'

    def __compile_multiple_var_names(self, kind=VAR) -> None:
        """
        Compiles multiple varNames sequence.

        type varName (',' varName)*
        """
        type = self.__get_cur_token()
        self.tokenizer.advance()
        self.table.define(self.__get_cur_token(), type, kind.upper())
        self.tokenizer.advance()

        while self.__get_cur_token() == COMMA:
            self.tokenizer.advance()
            self.table.define(self.__get_cur_token(), type, kind.upper())
            self.tokenizer.advance()

    def compile_class(self) -> None:
        """Compiles a complete class.

        'class' className '{' classVarDec* subroutineDec* '}'
        """
        self.tokenizer.advance()  # 'class'
        self.cur_class = self.__get_cur_token()
        # save the name of the current class
        self.tokenizer.advance()  # className
        self.tokenizer.advance()  # '{'

        while self.__is_var_dec():
            self.compile_class_var_dec()  # classVarDec

        while self.__is_subroutine():
            self.compile_subroutine()  # subroutineDec

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.

        ('static'|'field') type varName (',' varName)* ';'

        """
        kind = self.__get_cur_token()  # static/field
        self.tokenizer.advance()

        self.__compile_multiple_var_names(kind)

        self.tokenizer.advance()

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor.

        ('constructor'|'function'|'method') ('void'|type) subroutineName
        '(' parameterList '); subroutineBody

        """
        self.table.start_subroutine()

        routine_type = self.__get_cur_token()
        self.tokenizer.advance()

        # don't need to save return type since this can be inferred from
        # the return statement
        self.tokenizer.advance()

        subroutine_name = self.__get_cur_token()
        self.tokenizer.advance()  # subroutineName

        if routine_type == "method":
            self.table.define("this", self.cur_class, ARG)

        self.compile_parameter_list()  # parameterList
        self.tokenizer.advance()  # for '{'
        while self.__get_cur_token() == "var":
            self.compile_var_dec()  # varDec
        self.vm_writer.write_function(self.cur_class + PERIOD +
                                      subroutine_name,
                                      self.table.var_count(VAR))

        if routine_type == "constructor":
            self.__compile_constructor(self.table.var_count(FIELD))
            # call with the number of field arguments
        elif routine_type == "method":
            self.vm_writer.write_push(ARG, 0)
            self.vm_writer.write_pop(POINTER, 0)

        self.compile_statements()  # statements

        self.tokenizer.advance()  # '}'

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".

        '('type varName (',' type varName)*? ')'
        """
        # Note: parameterList only within context of subroutineDec,
        # this cond allows to determine whether List is empty
        self.tokenizer.advance()  # advance for '('

        if self.__get_cur_token() != CLOSE_PAREN:
            type = self.__get_cur_token()
            self.tokenizer.advance()
            self.table.define(self.__get_cur_token(), type, ARG)
            self.tokenizer.advance()

            while self.__get_cur_token() == COMMA:
                self.tokenizer.advance()
                type = self.__get_cur_token()
                self.tokenizer.advance()
                self.table.define(self.__get_cur_token(), type, ARG)
                self.tokenizer.advance()

        self.tokenizer.advance()  # advance for ')'

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.

        'var' type varName (',' varName)* ';'
        """
        self.tokenizer.advance()  # for 'var'

        self.__compile_multiple_var_names()  # type varName (',' varName)* ';'

        self.tokenizer.advance()  # for ';'

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".

        statement*
        """
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

    def compile_do(self) -> None:
        """Compiles a do statement.

        'do' subroutineCall ';'
        """
        self.tokenizer.advance()  # do
        self.__compile_subroutine_call()  # subroutineCall
        self.vm_writer.write_pop(TEMP, 0)
        self.tokenizer.advance()  # ';'

    def compile_let(self) -> None:
        """Compiles a let statement.

        'let' varName ('[' expression ']')? '=' expression ';'
        """
        self.tokenizer.advance()  # 'let'

        name = self.__get_cur_token()  # gets varName
        type, kind, index = self.__lookup_table(name)

        self.tokenizer.advance()

        if self.__get_cur_token() == OPEN_SQUARE:
            self.vm_writer.write_push(segments[kind], index)
            self.tokenizer.advance()  # '['
            self.compile_expression()  # exp1
            self.tokenizer.advance()  # ']'
            self.vm_writer.write_arithmetic(ADD)
            self.tokenizer.advance()  # '='
            self.compile_expression()  # exp2
            self.vm_writer.write_pop(TEMP, 0)
            self.vm_writer.write_pop(POINTER, 1)
            self.vm_writer.write_push(TEMP, 0)
            self.vm_writer.write_pop(THAT, 0)
        else:
            self.tokenizer.advance()  # '='
            self.compile_expression()  # expression
            self.vm_writer.write_pop(segments[kind], index)

        self.tokenizer.advance()  # ';'

    def compile_while(self) -> None:
        """Compiles a while statement.

        'while' '(' expression ')' '{' statements '}'
        """
        this_while_counter = str(self.while_counter)
        self.while_counter += 1

        label1 = WHILE + PERIOD + L1 + PERIOD + this_while_counter
        label2 = WHILE + PERIOD + L2 + PERIOD + this_while_counter

        self.tokenizer.advance()  # 'while'

        self.vm_writer.write_label(label1)

        self.tokenizer.advance()  # '('
        self.compile_expression()  # expression
        self.tokenizer.advance()  # ')'
        self.vm_writer.write_arithmetic(NOT)
        self.vm_writer.write_if(label2)

        self.tokenizer.advance()  # '{'
        self.compile_statements()  # expression
        self.tokenizer.advance()  # '}'

        self.vm_writer.write_goto(label1)
        self.vm_writer.write_label(label2)

    def compile_return(self) -> None:
        """Compiles a return statement.

        'return' expression? ';'
        """
        self.tokenizer.advance()

        if self.__get_cur_token() == SEMICOLON:
            self.vm_writer.write_push(CONST, 0)
        else:
            self.compile_expression()  # expression

        self.vm_writer.write_return()
        self.tokenizer.advance()  # ';'

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause.

        'if' '(' expression ')' '{' statements '}'
        ('else' '{' statements '}')?
        """
        this_if_counter = str(self.if_counter)
        self.if_counter += 1

        label1 = IF + PERIOD + L1 + PERIOD + this_if_counter
        label2 = IF + PERIOD + L2 + PERIOD + this_if_counter

        self.tokenizer.advance()  # 'if'
        self.tokenizer.advance()  # '('
        self.compile_expression()  # expression
        self.vm_writer.write_arithmetic(NOT)
        self.vm_writer.write_if(label1)
        self.tokenizer.advance()  # ')'

        self.tokenizer.advance()  # '{'
        self.compile_statements()  # statements
        self.vm_writer.write_goto(label2)
        self.tokenizer.advance()  # '}'

        self.vm_writer.write_label(label1)

        if self.__get_cur_token() == "else":
            self.tokenizer.advance()  # 'else'
            self.tokenizer.advance()  # '{'
            self.compile_statements()  # statements
            self.tokenizer.advance()  # '}'

        self.vm_writer.write_label(label2)

    def compile_expression(self) -> None:
        """Compiles an expression.

        term (op term)*
        """
        self.compile_term()

        while self.__get_cur_token() in ops:
            operator = self.__get_cur_token()
            self.tokenizer.advance()
            self.compile_term()
            if operator == '/':
                self.vm_writer.write_call("Math.divide", 2)
            elif operator == '*':
                self.vm_writer.write_call("Math.multiply", 2)
            else:
                self.vm_writer.write_arithmetic(ops[operator])

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
        if self.__get_cur_token() == OPEN_PAREN:
            self.tokenizer.advance()  # '('
            self.compile_expression()
            self.tokenizer.advance()  # ')'
        elif self.tokenizer.token_type() == atoms[IDENTIFIER]:  # varName
            self.compile_varname()
        elif self.tokenizer.token_type() == atoms[STRING_CONST]:
            self.compile_string_constant()
        elif self.tokenizer.token_type() == atoms[INT_CONST]:
            self.compile_int_constant()
        elif self.__get_cur_token() in keyword_constants:
            self.compile_keyword_constant()
        elif self.__get_cur_token() in unary_ops:
            self.compile_unary_op()

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions.

        (expression (',' expression)* )?
        """
        num_of_args = 0
        # Note: parameterList only withing context of subroutineDec,
        # this mechanism allows to determine whether List is empty
        if self.__get_cur_token() != CLOSE_PAREN:
            self.compile_expression()  # expression
            num_of_args += 1
            while self.__get_cur_token() == COMMA:
                self.tokenizer.advance()  # ','
                self.compile_expression()  # expression
                num_of_args += 1

        return num_of_args

    def __compile_constructor(self, num_of_args) -> None:
        self.vm_writer.write_push(CONST, num_of_args)
        self.vm_writer.write_call("Memory.alloc", 1)
        self.vm_writer.write_pop(POINTER, 0)

    def compile_varname(self):
        name = self.__get_cur_token()
        self.tokenizer.advance()
        # varname is a call to a subroutine
        if self.__get_cur_token() == '(' or self.__get_cur_token() == '.':
            self.__compile_subroutine_call(name)
        else:
            # varname is NOT a known variable in the current scope
            if not self.table.contains(name):
                self.vm_writer.write_push(ARG, 0)
            else:
                type, kind, index = self.__lookup_table(name)
                self.vm_writer.write_push(segments[kind], index)

            if self.__get_cur_token() == OPEN_SQUARE:
                self.tokenizer.advance()  # '['
                self.compile_expression()  # exp1
                self.tokenizer.advance()  # ']'
                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop(POINTER, 1)
                self.vm_writer.write_push(THAT, 0)

    def compile_unary_op(self):
        operation = self.__get_cur_token()
        self.tokenizer.advance()
        self.compile_term()
        self.vm_writer.write_arithmetic(unary_ops[operation])

    def compile_string_constant(self):
        string = self.__get_cur_token()
        self.vm_writer.write_push(CONST, len(string))
        self.vm_writer.write_call("String.new", 1)
        for char in string:
            self.vm_writer.write_push(CONST, ord(char))
            self.vm_writer.write_call("String.appendChar", 2)

        self.tokenizer.advance()

    def compile_int_constant(self):
        self.vm_writer.write_push(CONST, self.__get_cur_token())
        self.tokenizer.advance()

    def compile_keyword_constant(self):
        token = self.__get_cur_token()
        if token == "true":
            self.vm_writer.write_push(CONST, 0)
            self.vm_writer.write_arithmetic(NOT)
        elif token == "false" or token == "null":
            self.vm_writer.write_push(CONST, 0)
        elif token == "this":
            self.vm_writer.write_push(POINTER, 0)

        self.tokenizer.advance()

    def __lookup_table(self, name):
        return self.table.type_of(name), self.table.kind_of(name), \
               self.table.index_of(name)
