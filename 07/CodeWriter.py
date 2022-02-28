"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

NEWLINE, COMMENT_START, SPACE, PERIOD = "\n", "//", ' ', '.'
R13, R14, M_TO_A, SEQUENCE_END, SAME_SIGNS, DIFF_SIGNS = \
    "R13", "R14", "A=M\n", "SEQUENCE_END{0}", "SAME_SIGNS{0}", "DIFF_SIGNS{0}"

POP_STACK_TO_D, POP_STACK_ADD_TO_D, PUSH_D_TO_STACK, NEG_D, \
IF_COND_D_TRUE_ELSE_FALSE, POP_STACK_LOGICAL_D_TO_D, NOT_D, \
CONSTANT_TO_D, ADDRESS_TO_CONTAINER, STAR_CONTAINER_TO_D, \
D_TO_STAR_CONTAINER, CONTAINER_TO_D, D_TO_CONTAINER, SHIFT_D, \
OVERFLOW_PREVENTION_LOGIC, ADD_CONTAINER_TO_D, \
UNCONDITIONAL_JUMP, NEW_LABEL = range(18)

POP, PUSH, RELATIONAL, LOGICAL, EQ, GT, LT, AND, OR, NOT, CONSTANT, \
ADD, SUB, NEG, SHIFT_LEFT, SHIFT_RIGHT, SHIFT, STATIC, STATIC_PTR = \
    "C_POP", "C_PUSH", "relational", "logical", "eq", "gt", "lt", "and", \
    "or", "not", "constant", "add", "sub", "neg", "shiftleft", \
    "shiftright", "shift", "static", "static-ptr"

segment_dict = {"local": "LCL", "argument": "ARG", "this": "THIS",
                "that": "THAT", "temp": '5', 0: "THIS", 1: "THAT"}

commands = {
    POP_STACK_TO_D: "@SP\n"
                    "M=M-1\n"
                    "@SP\n"
                    "A=M\n"
                    "D=M\n",
    POP_STACK_ADD_TO_D: "@SP\n"
                        "M=M-1\n"
                        "@SP\n"
                        "A=M\n"
                        "D=D+M\n",
    PUSH_D_TO_STACK: "@SP\n"
                     "A=M\n"
                     "M=D\n"
                     "@SP\n"
                     "M=M+1\n",
    NEG_D: "D=-D\n",
    IF_COND_D_TRUE_ELSE_FALSE: "@COND{0}\n"  # self.cond_ctr
                               "{1}\n"  # condition (from dict)
                               "D=0\n"
                               "@END{0}\n"
                               "0;JMP\n"
                               "(COND{0})\n"
                               "D=-1\n"
                               "(END{0})\n",
    POP_STACK_LOGICAL_D_TO_D: "@SP\n"
                              "M=M-1\n"
                              "@SP\n"
                              "A=M\n"
                              "{}\n",  # condition (from dict)
    NOT_D: "D=!D\n",
    CONSTANT_TO_D: "@{}\n"  # constant
                   "D=A\n",
    ADDRESS_TO_CONTAINER: "@{}\n"  # index  
                          "D=A\n"
                          "@{}\n"  # base_address
                          "{}"  # A=M\n
                          "D=D+A\n"
                          "@{}\n"  # container
                          "M=D\n",
    STAR_CONTAINER_TO_D: "@{}\n"  # container
                         "A=M\n"
                         "D=M\n",
    D_TO_STAR_CONTAINER: "@{}\n"  # container
                         "A=M\n"
                         "M=D\n",
    CONTAINER_TO_D: "@{}\n"  # container
                    "D=M\n",
    D_TO_CONTAINER: "@{}\n"  # container
                    "M=D\n",
    SHIFT_D: "D=D{}\n",  # shift
    OVERFLOW_PREVENTION_LOGIC: "@R13\n"
                               "D=M\n"
                               "@FIRST_VAL_POS{0}\n"  # self.cond_ctr
                               "D;JGE\n"
                               "(FIRST_VAL_NEG{0})\n"
                               "@R14\n"
                               "D=M\n"
                               "@SAME_SIGNS{0}\n"
                               "D;JLE\n"
                               "@DIFF_SIGNS{0}\n"
                               "0;JMP\n"
                               "(FIRST_VAL_POS{0})\n"
                               "@R14\n"
                               "D=M\n"
                               "@SAME_SIGNS{0}\n"
                               "D;JGE\n",
    ADD_CONTAINER_TO_D: "@{}\n"  # container
                        "D=D+M\n",
    UNCONDITIONAL_JUMP: "@{}\n"  # label
                        "0;JMP\n",
    NEW_LABEL: "({})\n",  # label
}

relational_conditions = {EQ: "D;JEQ", GT: "D;JGT", LT: "D;JLT"}
logical_conditions = {AND: "D=D&M", OR: "D=D|M"}
shifts = {SHIFT_LEFT: "<<", SHIFT_RIGHT: ">>"}

asm = {
    # No .format() needed, use as is
    ADD: commands[POP_STACK_TO_D] +
         commands[POP_STACK_ADD_TO_D] +
         commands[PUSH_D_TO_STACK],
    SUB: commands[POP_STACK_TO_D] +
         commands[NEG_D] +
         commands[POP_STACK_ADD_TO_D] +
         commands[PUSH_D_TO_STACK],
    NEG: commands[POP_STACK_TO_D] +
         commands[NEG_D] +
         commands[PUSH_D_TO_STACK],
    NOT: commands[POP_STACK_TO_D] +
         commands[NOT_D] +
         commands[PUSH_D_TO_STACK],

    # Usage: .format(shift_type)
    SHIFT: commands[POP_STACK_TO_D] +
           commands[SHIFT_D] +
           commands[PUSH_D_TO_STACK],

    # Usage: .format(constant)
    CONSTANT: commands[CONSTANT_TO_D] +
              commands[PUSH_D_TO_STACK],

    # Usage: .format.(self.cond_ctr, condition)
    # Note - The long logic is a result of possible integer overflow.
    RELATIONAL: commands[POP_STACK_TO_D] +
                commands[D_TO_CONTAINER].format(R14) +
                commands[POP_STACK_TO_D] +
                commands[D_TO_CONTAINER].format(R13) +
                commands[OVERFLOW_PREVENTION_LOGIC] +

                # DIFFERENT signs logic
                commands[NEW_LABEL].format(DIFF_SIGNS) +
                commands[CONTAINER_TO_D].format(R13) +
                commands[IF_COND_D_TRUE_ELSE_FALSE] +
                commands[PUSH_D_TO_STACK] +
                commands[UNCONDITIONAL_JUMP].format(SEQUENCE_END) +

                # SAME signs logic
                commands[NEW_LABEL].format(SAME_SIGNS) +
                commands[CONTAINER_TO_D].format(R14) +
                commands[NEG_D] +
                commands[ADD_CONTAINER_TO_D].format(R13) +
                commands[IF_COND_D_TRUE_ELSE_FALSE] +
                commands[PUSH_D_TO_STACK] +

                commands[NEW_LABEL].format(SEQUENCE_END),

    # Usage: .format(condition)
    LOGICAL: commands[POP_STACK_TO_D] +
             commands[POP_STACK_LOGICAL_D_TO_D] +
             commands[PUSH_D_TO_STACK],

    # Usage: .format(index, base_address, "A=M\n", temp_container,
    #                temp_container)
    PUSH: commands[ADDRESS_TO_CONTAINER] +
          commands[STAR_CONTAINER_TO_D] +
          commands[PUSH_D_TO_STACK],
    POP: commands[ADDRESS_TO_CONTAINER] +
         commands[POP_STACK_TO_D] +
         commands[D_TO_STAR_CONTAINER],

    # Usage: .format(static_var (for static) \ base_address (for pointer))
    STATIC_PTR: {PUSH: commands[CONTAINER_TO_D] +
                       commands[PUSH_D_TO_STACK],
                 POP: commands[POP_STACK_TO_D] +
                      commands[D_TO_CONTAINER]},
}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output_stream = output_stream
        self.vm_filename = ''
        self.cond_ctr = 0

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.vm_filename = filename

    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        # eq, gt, lt
        if command in relational_conditions:
            condition = relational_conditions[command]
            asm_code = asm[RELATIONAL].format(self.cond_ctr, condition)
            self.cond_ctr += 1
        # and, or
        elif command in logical_conditions:
            condition = logical_conditions[command]
            asm_code = asm[LOGICAL].format(condition)
        # shiftleft, shiftright
        elif command in shifts:
            asm_code = asm[SHIFT].format(shifts[command])
        # add, sub, neg, not
        else:
            asm_code = asm[command]

        # Generate comment
        comment = COMMENT_START + command + SPACE + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        # constant
        if segment == CONSTANT:
            asm_code = asm[CONSTANT].format(index)
        # local, argument, this, that, temp
        elif segment in segment_dict:
            base_address = segment_dict[segment]
            # Exclude temp, since 5 is the actual offset (not a ptr to offset)
            m_to_a = M_TO_A if base_address != '5' else ''
            asm_code = asm[command].format(index, base_address, m_to_a, R13,
                                           R13)
        # static
        elif segment == STATIC:
            static_var = self.__generate_static_var(index)
            asm_code = asm[STATIC_PTR][command].format(static_var)
        # pointer
        else:
            base_address = index if index not in segment_dict \
                else segment_dict[index]
            asm_code = asm[STATIC_PTR][command].format(base_address)

        # Generate comment
        comment = COMMENT_START + command + SPACE + segment + SPACE + str(
            index) + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()

    def __generate_static_var(self, index: int) -> str:
        """ Generates the appropriate static variable label.

         Args:
             index (int): index within the static segment.
         """
        return self.vm_filename + PERIOD + str(index)
