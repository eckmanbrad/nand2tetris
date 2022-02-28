"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.commands = []

        input_lines = input_file.read().splitlines()
        for line in input_lines:
            # Erase comments
            comment_ind = line.find("//")
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
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true.
        Initially there is no current command.
        """
        self.cur_command_ind += 1
        self.cur_command = self.commands[self.cur_command_ind]

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        first_word_dict = {"add": "C_ARITHMETIC", "sub": "C_ARITHMETIC",
                           "neg": "C_ARITHMETIC", "eq": "C_ARITHMETIC",
                           "shiftleft": "C_ARITHMETIC",
                           "shiftright": "C_ARITHMETIC",
                           "gt": "C_ARITHMETIC", "lt": "C_ARITHMETIC",
                           "and": "C_ARITHMETIC", "or": "C_ARITHMETIC",
                           "not": "C_ARITHMETIC",
                           "push": "C_PUSH", "pop": "C_POP",
                           "label": "C_LABEL", "goto": "C_GOTO",
                           "if-goto": "C_IF", "function": "C_FUNCTION",
                           "return": "C_RETURN", "call": "C_CALL"}

        return first_word_dict[self.cur_command.split()[0]]

    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        args = self.cur_command.split()
        arg_index = 0 if self.command_type() == "C_ARITHMETIC" else 1

        return args[arg_index]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.cur_command.split().pop())
