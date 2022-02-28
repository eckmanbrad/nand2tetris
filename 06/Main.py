"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

ZERO = '0'


def decimal_to_binary_str(num) -> str:
    """Writes list of commands to supplied output file.

    Args:
        num: a number formatted as a string.

    Returns:
        str: 16-bit binary (base 2) representation of num
    """
    temp_bin_str = bin(int(num))
    temp_bin_str = temp_bin_str[2:]  # strip leading "0b"
    # Complete to 16 bits
    n = 15 - len(temp_bin_str)
    return (ZERO * n) + temp_bin_str


def translate_a_command(parser, symbol_table, next_free_register) -> str:
    """Translates an A-Command to machine code.

    Args:
        parser: A Parser object
        symbol_table: The current symbol table
        next_free_register: The address of the next available RAM register

    Returns:
        str: The current command in machine code.
    """
    symbol = parser.symbol()
    # Check if symbol is indeed a symbol, or a number
    if symbol.isnumeric():
        return ZERO + decimal_to_binary_str(symbol)
    # Update symbol table if needed
    if not symbol_table.contains(symbol):
        symbol_table.add_entry(symbol, next_free_register[0])
        next_free_register[0] += 1

    address = symbol_table.get_address(symbol)
    return ZERO + decimal_to_binary_str(address)


def translate_c_command(parser, code) -> str:
    """Translates a C-Command to machine code.

    Args:
        parser: A Parser object
        code: A Code object

    Returns:
        str: The current command in machine code.
    """
    # Decode by mapping the relevant bits
    dest = code.dest(parser.dest())
    comp = code.comp(parser.comp())
    jump = code.jump(parser.jump())
    prefix = code.prefix(parser.comp())

    return prefix + comp + dest + jump


def first_pass(parser, symbol_table) -> None:
    """Initiates the first pass on the given symbolic code.

    Args:
        parser: A Parser object
        symbol_table: The current symbol table
    """
    cur_rom_address = 0
    while parser.has_more_commands():
        parser.advance()
        com_type = parser.command_type()
        # If label, update symbol table if needed
        if com_type == "L_COMMAND":
            if not symbol_table.contains(parser.symbol()):
                symbol_table.add_entry(parser.symbol(), cur_rom_address)
        else:
            cur_rom_address += 1


def second_pass(parser, symbol_table, output_commands) -> None:
    """Initiates the second pass on the given symbolic code.

    Args:
        parser: A Parser object
        symbol_table: The current symbol table
        output_commands: The list of commands translated into machine code
    """
    code = Code()
    next_free_register = [16]  # need mutable data type

    while parser.has_more_commands():
        parser.advance()
        com_type = parser.command_type()
        if com_type == "A_COMMAND":
            output_commands.append(translate_a_command(parser, symbol_table,
                                                       next_free_register))
        if com_type == "C_COMMAND":
            output_commands.append(translate_c_command(parser, code))


def write_to_output_file(output_commands, output_file) -> None:
    """Writes list of commands to supplied output file.

    Args:
        output_commands: list of translated binary commands.
        output_file: writes all output to this file.
    """
    for command in output_commands:
        output_file.write(command + "\n")


def assemble_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """

    # Initialize symbol table and binary command list
    symbol_table = SymbolTable()
    output_commands = []

    # Initiate two-pass processing of the input file
    first_pass_parser = Parser(input_file)
    input_file.seek(0)
    second_pass_parser = Parser(input_file)

    first_pass(first_pass_parser, symbol_table)
    second_pass(second_pass_parser, symbol_table, output_commands)

    # Write translated commands to output file
    write_to_output_file(output_commands, output_file)


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
