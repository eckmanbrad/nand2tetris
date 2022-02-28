"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST = \
    "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"

keywords = ["class", "constructor", "function", "method", "field", "static",
            "var", "int", "char", "boolean", "void", "true", "false", "null",
            "this", "let", "do", "if", "else", "while", "return"]

symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
           '&', '|', '<', '>', '=', '~', '^', "#"]


def is_string_constant(word):
    """ Is the provided word an string constant? """
    return word[0] == '"' and word[-1] == '"'


def is_symbol(char):
    """ Is the provided char a symbol? """
    return char in symbols


def is_int_constant(word):
    """ Is the provided word an integer constant? """
    return word.isnumeric()


def erase_comments(text):
    """
    Erases comments from text.

    Args:
        text (str) - The text to erase the comments from
    """
    cleaned_lines = []
    in_string = False
    in_comment = False

    # Iterate over lines and erase comments
    for line in text:
        clean_line = ""

        index = 0
        while index < len(line):
            is_comment_closer = False

            if line[index] == '"' and not in_comment:
                in_string = not in_string
            if index < len(line) - 1 and not in_string:
                if line[index:index+2] == "//" and not in_comment:
                    break
                if line[index:index+2] == "/*" and not in_comment:
                    in_comment = True
                    index += 1
                if line[index:index + 2] == "*/" and in_comment:
                    in_comment = False
                    is_comment_closer = True
                    index += 1

            if not is_comment_closer and not in_comment:
                clean_line += line[index]

            index += 1

        clean_line = clean_line.strip()
        if clean_line:
            cleaned_lines.append(clean_line)

    return cleaned_lines


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        input_lines = input_stream.read().splitlines()
        self.lines = erase_comments(input_lines)

        self.line_ind = 0
        self.char_ind = 0

        self.cur_token = ""

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return False if self.line_ind == len(self.lines) - 1 and self. \
            char_ind >= len(self.lines[self.line_ind]) - 1 else True

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Move to next line if needed
        if self.char_ind >= len(self.__get_cur_line()):
            self.line_ind += 1
            self.char_ind = 0
        # Skip over spaces until reaching a char
        self.__skip_spaces()
        first_char = self.__get_cur_line()[self.char_ind]

        # Next token is a stringConstant
        if first_char == '"':
            end = self.__get_cur_line().find('"', self.char_ind + 1)
            self.__update_cur_token(end + 1)
        # Next token is integerConstant
        elif first_char.isnumeric():
            end = self.char_ind + 1
            for char in self.__get_cur_line()[end:]:
                if not char.isnumeric():
                    break
                end += 1
            self.__update_cur_token(end)
        # Next token is a symbol
        elif first_char in symbols:
            self.__update_cur_token(self.char_ind + 1)
        # Next token is either a keyword or an identifier - find the next
        # symbol or next space
        else:
            end = self.char_ind + 1
            for char in self.__get_cur_line()[end:]:
                if char in symbols or char == ' ':
                    break
                end += 1
            self.__update_cur_token(end)

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in keywords:
            return KEYWORD
        elif self.cur_token in symbols:
            return SYMBOL
        elif is_int_constant(self.cur_token):
            return INT_CONST
        elif is_string_constant(self.cur_token):
            return STRING_CONST
        else:
            return IDENTIFIER

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.cur_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.cur_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.cur_token[1:-1]

    def __get_cur_line(self):
        """ Gets the current line. """
        return self.lines[self.line_ind]

    def __skip_spaces(self):
        """ Skips all spaces until the next non-space character. """
        while self.__get_cur_line()[self.char_ind] == ' ':
            self.char_ind += 1

    def __update_cur_token(self, end):
        """ Updates the current token. """
        self.cur_token = self.__get_cur_line()[self.char_ind:end]
        self.char_ind = end