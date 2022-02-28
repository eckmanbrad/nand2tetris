"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

NEWLINE = '\n'

CONST, ARG, LOCAL, STATIC, THIS, THAT, POINTER, TEMP = "CONST", "ARG", \
      "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"

PUSH, POP, ADD, SUB, NEG, EQ, GT, LT, AND, OR, NOT, LABEL, GOTO, IF, CALL, \
    FUNCTION, RETURN, SHIFTLEFT, SHIFTRIGHT = "PUSH", "POP", "ADD", "SUB", \
    "NEG", "EQ", "GT", "LT", "AND", "OR", "NOT", "LABEL", "GOTO", "IF", \
    "CALL", "FUNCTION", "RETURN", "SHIFTLEFT", "SHIFTRIGHT"

commands = {
    # Usage: .format(segment, index)
    PUSH: "push {} {}",
    # Usage: .format(segment, index)
    POP: "pop {} {}",
    # Arithmetic commands (use as is, no .format needed)
    # ADD: "add", SUB: "sub", NEG: "neg", EQ: "eq", GT: "gt", LT: "lt",
    # AND: "and", OR: "or", NOT: "not", SHIFTLEFT: "shiftleft", SHIFTRIGHT:
    #     "shiftright",
    # Program-flow commands. Usage: .format(label)
    LABEL: "label {}", GOTO: "goto {}", IF: "if-goto {}",
    # Function commands. Usage: .format(label, num_of_vars)
    CALL: "call {} {}", FUNCTION: "function {} {}",
    # Return command (use as is, no .format needed)
    RETURN: "return"
}

segments = {CONST: "constant", ARG: "argument", LOCAL: "local",
            STATIC: "static", THIS: "this", THAT: "that",
            POINTER: "pointer", TEMP: "temp"}


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output_file = open(output_stream.name, 'w')

    def __write_to_output(self, text):
        self.output_file.write(text + NEWLINE)

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        self.__write_to_output(commands[PUSH].format(segments[segment],
                                                     str(index)))

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        self.__write_to_output(commands[POP].format(segments[segment],
                                                    str(index)))

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB", "NEG", 
            "EQ", "GT", "LT", "AND", "OR", "NOT", "SHIFTLEFT", "SHIFTRIGHT.
        """
        self.__write_to_output(command.lower())

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.__write_to_output(commands[LABEL].format(label))

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.__write_to_output(commands[GOTO].format(label))

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.__write_to_output(commands[IF].format(label))

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.__write_to_output(commands[CALL].format(name, n_args))

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.__write_to_output(commands[FUNCTION].format(name, n_locals))

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.__write_to_output(commands[RETURN])

    def close(self) -> None:
        """Closes the output file."""
        self.output_file.close()
