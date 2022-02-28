"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

SPACE, START_COMMENT, L_PAREN, R_PAREN, AT, EQUALS, SEMICOLON = \
    ' ', "//", '(', ')', '@', '=', ';'


class Parser:
    """Encapsulates access to the input code. Reads an assembly language
    command, parses it, and provides convenient access to the commands 
    components (fields and symbols). In addition, removes all white space and 
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.commands = []

        input_lines = input_file.read().splitlines()
        for line in input_lines:
            # Erase comments
            comment_ind = line.find(START_COMMENT)
            if comment_ind != -1:
                line = line[:comment_ind]
            # Erase whitespace
            line = line.strip()
            if line:
                self.commands.append(line)

        self.cur_command = ""
        self.cur_command_ind = -1
        self.num_of_commands = len(self.commands)

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_command_ind < self.num_of_commands - 1

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        self.cur_command_ind += 1
        self.cur_command = self.commands[self.cur_command_ind]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.cur_command[0] == AT:
            return "A_COMMAND"
        elif self.cur_command[0] == L_PAREN and \
                self.cur_command[-1] == R_PAREN:
            return "L_COMMAND"
        else:
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        com_type = self.command_type()
        if com_type == "A_COMMAND":
            return self.cur_command[1:]  # exclude @
        if com_type == "L_COMMAND":
            return self.cur_command[1:-1]  # exclude parentheses

    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        end_ind = self.cur_command.find(EQUALS)

        if end_ind != -1:
            return self.cur_command[:end_ind].replace(SPACE, "")
        return ""

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        start_ind = self.cur_command.find(EQUALS) + 1
        end_ind = self.cur_command.find(SEMICOLON)

        if start_ind != 0 and end_ind != -1:
            return self.cur_command[start_ind:end_ind].replace(SPACE, "")
        elif start_ind != 0:
            return self.cur_command[start_ind:].replace(SPACE, "")
        else:
            return self.cur_command[:end_ind].replace(SPACE, "")

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        start_ind = self.cur_command.find(SEMICOLON) + 1

        if start_ind != 0:
            return self.cur_command[start_ind:].replace(SPACE, "")
        return ""
