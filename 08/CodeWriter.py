"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

NEWLINE, COMMENT_START, SPACE, PERIOD, DOLLAR = "\n", "// ", " ", '.', '$'
SP, LCL, ARG, THIS, THAT, R13, R14, R15, DFLT_SP, RET_FORMAT, M_TO_A, \
SEQUENCE_END, SAME_SIGNS, DIFF_SIGNS = \
    "SP", "LCL", "ARG", "THIS", "THAT", "R13", "R14", "R15", "256", ".ret$", \
    "A=M\n", "SEQUENCE_END{0}", "SAME_SIGNS{0}", "DIFF_SIGNS{0}"

POP_STACK_TO_D, POP_STACK_ADD_TO_D, PUSH_D_TO_STACK, NEG_D, \
IF_COND_D_TRUE_ELSE_FALSE, POP_STACK_LOGICAL_D_TO_D, NOT_D, \
CONSTANT_TO_D, ADDRESS_TO_CONTAINER, STAR_CONTAINER_TO_D, \
D_TO_STAR_CONTAINER, CONTAINER_TO_D, D_TO_CONTAINER, SHIFT_D, \
OVERFLOW_PREVENTION_LOGIC, ADD_CONTAINER_TO_D, UNCONDITIONAL_JUMP, \
NEW_LABEL, ADDRESS_JUMP, IF_D_JMP_TO_LABEL, SP_SUB_FIVE_SUB_NARGS_TO_D, \
GENERIC_LOOP, X_SUB_Y_TO_D, INC_ARG_TO_SP = range(24)

POP, PUSH, RELATIONAL, LOGICAL, EQ, GT, LT, AND, OR, NOT, CONSTANT, ADD, \
SUB, NEG, SHIFT_LEFT, SHIFT_RIGHT, SHIFT, STATIC, STATIC_PTR, \
BOOTSTRAP, LABEL, GOTO, IF_GOTO, RESTORE_ADDR, PUSH_CONTAINER, LOOP, \
FUNCTION, CALL, RETURN = \
    "C_POP", "C_PUSH", "relational", "logical", "eq", "gt", "lt", "and", \
    "or", "not", "constant", "add", "sub", "neg", "shiftleft", "shiftright", \
    "shift", "static", "static-pointer", "bootstrap", "label", "goto", \
    "if-goto", "restore", "push*", "loop", "function", "call", "return"

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
    ADDRESS_JUMP: "@{}\n"  # jump_address
                  "{}"  # A=M\n
                  "0;JMP\n",
    IF_D_JMP_TO_LABEL: "@{}\n"  # label
                       "D+1;JEQ\n",
    SP_SUB_FIVE_SUB_NARGS_TO_D: "@SP\n"
                                "D=M\n"
                                "@5\n"
                                "D=D-A\n"
                                "@{}\n"  # nArgs
                                "D=D-A\n",
    GENERIC_LOOP: "@{0}\n"  # num_of_iterations
                  "D=A\n"
                  "@R14\n"
                  "M=D\n"
                  "(LOOP{1})\n"  # self.loop_ctr
                  "@R14\n"
                  "D=M\n"
                  "@BREAK{1}\n"
                  "D;JEQ\n"
                  "{2}"  # loop_action
                  "@R14\n"
                  "M=M-1\n"
                  "@LOOP{1}\n"
                  "0;JMP\n"
                  "(BREAK{1})\n",
    X_SUB_Y_TO_D: "@{}\n"  # container_of_address_of_x
                  "D=M\n"
                  "@{}\n"  # y
                  "D=D-A\n",
    INC_ARG_TO_SP: "@ARG\n"
                   "D=M\n"
                   "@SP\n"
                   "M=D+1\n"
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

    # Usage: .format("256", container)
    BOOTSTRAP: commands[CONSTANT_TO_D] +
               commands[D_TO_CONTAINER],

    # Usage: .format(label)
    LABEL: commands[NEW_LABEL],

    # Usage: .format(rom_address, "A=M\n")
    GOTO: commands[ADDRESS_JUMP],

    # Usage: .format(label)
    IF_GOTO: commands[POP_STACK_TO_D] +
             commands[IF_D_JMP_TO_LABEL],

    # Usage: .format(register, value, destination)
    #        arg[2] = arg[0] - arg[1]
    #        arg[3] = *(arg[2])
    RESTORE_ADDR: commands[X_SUB_Y_TO_D] + \
                  commands[D_TO_CONTAINER].format(R13) + \
                  commands[STAR_CONTAINER_TO_D].format(R13) + \
                  commands[D_TO_CONTAINER],

    # Usage: .format(container)
    PUSH_CONTAINER: commands[CONTAINER_TO_D] +
                    commands[PUSH_D_TO_STACK],

    # Usage: .format(num_of_iterations, self.loop_ctr, action)
    LOOP: commands[GENERIC_LOOP]
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
        self.cur_func = ''
        self.cond_ctr = 0
        self.loop_ctr = 0
        self.i = -1

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is 
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.vm_filename = filename

    def write_init(self):
        """ Writes the bootstrap assembly code to the output file. """
        comment = COMMENT_START + BOOTSTRAP + NEWLINE
        asm_code = asm[BOOTSTRAP].format(DFLT_SP, SP)
        self.output_stream.write(comment + asm_code + NEWLINE)
        self.write_call("Sys.init", 0)

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

    def write_label(self, label: str) -> None:
        """Writes the assembly code that is the translation of a label
        command.

        Args:
            label: The name of the label.
        """
        asm_code = asm[LABEL].format(self.__generate_label(label))
        self.output_stream.write(asm_code + NEWLINE)  # no comment

    def write_goto(self, label: str) -> None:
        """Writes the assembly code that is the translation of a goto command.

        Args:
            label: The name of the label to goto.
        """
        asm_code = asm[GOTO].format(self.__generate_label(label), '')
        comment = COMMENT_START + GOTO + SPACE + label + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def write_if(self, label: str) -> None:
        """Writes the assembly code that is the translation of an if-goto
        command.

        Args:
            label: The name of the label to goto if condition is met.
        """
        asm_code = asm[IF_GOTO].format(self.__generate_label(label))
        comment = COMMENT_START + IF_GOTO + SPACE + label + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def write_function(self, function_name: str, num_local_vars: int) -> None:
        """Writes the assembly code that is the translation of a function
        command.

        Args:
            function_name: The name of the function.
            num_local_vars: The number of local variables to create.
        """
        push_zero_asm = asm[CONSTANT].format(0)
        asm_code = asm[LABEL].format(function_name) + \
                   asm[LOOP].format(num_local_vars, self.loop_ctr,
                                    push_zero_asm)
        self.loop_ctr += 1
        comment = COMMENT_START + FUNCTION + SPACE + function_name + SPACE \
                  + str(num_local_vars) + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def write_call(self, function_name: str, num_args: int) -> None:
        """Writes the assembly code that is the translation of a call
        to a function.

        Args:
            function_name: The name of the function.
            num_args: The number of arguments the provided function expects.
        """
        self.cur_func = function_name
        self.i += 1
        ret_label = self.__generate_ret_label()

        # Push the return address and rest of frame to stack
        push_caller_frame_asm = asm[CONSTANT].format(ret_label) + \
                                asm[PUSH_CONTAINER].format(LCL) + \
                                asm[PUSH_CONTAINER].format(ARG) + \
                                asm[PUSH_CONTAINER].format(THIS) + \
                                asm[PUSH_CONTAINER].format(THAT)
        # Reposition ARG and LCL accordingly
        update_arg_asm = commands[SP_SUB_FIVE_SUB_NARGS_TO_D].format(
                                                                num_args) + \
                         commands[D_TO_CONTAINER].format(ARG)
        update_lcl_asm = commands[CONTAINER_TO_D].format(SP) + \
                         commands[D_TO_CONTAINER].format(LCL)
        # Go to the relevant function
        goto_function_asm = asm[GOTO].format(function_name, '')
        # Place return address label
        insert_label_asm = asm[LABEL].format(ret_label)

        asm_code = push_caller_frame_asm + update_arg_asm + \
                   update_lcl_asm + goto_function_asm + insert_label_asm + \
                   NEWLINE
        comment = COMMENT_START + CALL + SPACE + function_name + SPACE + \
                  str(num_args) + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def write_return(self) -> None:
        """Writes the assembly code that is the translation of a return
        command.
        """
        # Save the end frame (into R14)
        save_end_frame_asm = commands[CONTAINER_TO_D].format(LCL) + \
                             commands[D_TO_CONTAINER].format(R14)
        # Save the return address (into R15)
        save_ret_address_asm = asm[RESTORE_ADDR].format(R14, '5', R15)
        # Reposition return value and SP for caller
        pop_ret_value_asm = commands[POP_STACK_TO_D] + \
                            commands[D_TO_STAR_CONTAINER].format(ARG)
        update_sp_asm = commands[INC_ARG_TO_SP]
        # Restore caller frame
        restore_caller_frame_asm = \
            asm[RESTORE_ADDR].format(R14, '1', THAT) + \
            asm[RESTORE_ADDR].format(R14, '2', THIS) + \
            asm[RESTORE_ADDR].format(R14, '3', ARG) + \
            asm[RESTORE_ADDR].format(R14, '4', LCL)
        goto_ret_address_asm = asm[GOTO].format(R15, M_TO_A)

        asm_code = save_end_frame_asm + save_ret_address_asm + \
                   pop_ret_value_asm + update_sp_asm + \
                   restore_caller_frame_asm + goto_ret_address_asm + \
                   NEWLINE

        comment = COMMENT_START + RETURN + NEWLINE

        self.output_stream.write(comment + asm_code + NEWLINE)

    def close(self) -> None:
        """Closes the output file."""
        self.output_stream.close()

    def __generate_static_var(self, index: int) -> str:
        """Generates the appropriate static variable label.

         Args:
             index (int): index within the static segment.
         """
        return self.vm_filename + PERIOD + str(index)

    def __generate_label(self, label: str) -> str:
        """Generates the appropriate label.

         Args:
             label (str): The initial label string.
         """
        return self.vm_filename + PERIOD + self.cur_func + DOLLAR + label

    def __generate_ret_label(self) -> str:
        """Generates the appropriate return label."""
        return self.cur_func + RET_FORMAT + str(self.i)
