"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        dest_dict = {"": "000",
                     "M": "001",
                     "D": "010",
                     "MD": "011",
                     "A": "100",
                     "AM": "101",
                     "AD": "110",
                     "AMD": "111"}

        return dest_dict[mnemonic]

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 7-bit long binary code of the given mnemonic.
        """
        comp_code = "0"
        if mnemonic.find('M') != -1:  # a bit
            comp_code = '1'

        comp_dict = {"0": "101010",
                     "1": "111111",
                     "-1": "111010",
                     "D": "001100",
                     "A": "110000", "M": "110000",
                     "!D": "001101",
                     "!A": "110001", "!M": "110001",
                     "-D": "001111",
                     "-A": "110011", "-M": "110011",
                     "D+1": "011111",
                     "A+1": "110111", "M+1": "110111",
                     "D-1": "001110",
                     "A-1": "110010", "M-1": "110010",
                     "D+A": "000010", "D+M": "000010",
                     "D-A": "010011", "D-M": "010011",
                     "A-D": "000111", "M-D": "000111",
                     "D&A": "000000", "D&M": "000000",
                     "D|A": "010101", "D|M": "010101",
                     # Shift-additions
                     "D<<": "110000", "A<<": "100000", "M<<": "100000",
                     "D>>": "010000", "A>>": "000000", "M>>": "000000"}

        return comp_code + comp_dict[mnemonic]

    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        jump_dict = {"": "000",
                     "JGT": "001",
                     "JEQ": "010",
                     "JGE": "011",
                     "JLT": "100",
                     "JNE": "101",
                     "JLE": "110",
                     "JMP": "111"}

        return jump_dict[mnemonic]

    @staticmethod
    def prefix(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return "101" if ">>" in mnemonic or "<<" in mnemonic else "111"