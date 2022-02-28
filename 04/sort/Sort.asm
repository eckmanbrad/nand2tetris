// This file is part of nand2tetris, as taught in The Hebrew University,
// and was written by Aviv Yaish, and is published under the Creative 
// Common Attribution-NonCommercial-ShareAlike 3.0 Unported License 
// https://creativecommons.org/licenses/by-nc-sa/3.0/

// An implementation of a sorting algorithm. 
// An array is given in R14 and R15, where R14 contains the start address of the 
// array, and R15 contains the length of the array. 
// You are not allowed to change R14, R15.
// The program should sort the array in-place and in descending order - 
// the largest number at the head of the array.
// You can assume that each array value x is between -16384 < x < 16384.
// You can assume that the address in R14 is at least >= 2048, and that 
// R14 + R15 <= 16383. 
// No other assumptions can be made about the length of the array.
// You can implement any sorting algorithm as long as its runtime complexity is 
// at most C*O(N^2), like bubble-sort.

@i
M=0  // i = 0 (i is the outterloop iteration number))

@cur_address
M=0  // cur_address = 0 (cur_address = R14 + j, i.e. the current address)

@temp
M=0  // temp = 0 (temp will be used as a temporary container in SWAP)

@R15
D=M-1
@END
D;JEQ // if len(list)==1 goto END

(OUTTERLOOP)
    @R15
    D=M-1
    @i
    D=D-M
    @END
    D;JEQ // if i==len(list)-1 goto END

    @j
    M=0  // j = 0 (j is the current offset from the array's starting address)

    (INNERLOOP)
        @R15
        D=M-1
        @j
        D=D-M
        @OUTTERLOOP
        D;JEQ // if j==RAM[15]-1 goto (OUTTERLOOP)

        @R14
        D=M
        @j
        D=D+M
        @cur_address
        M=D  // cur_address = RAM[14] + j
    
        @cur_address
        A=M
        D=M
        @cur_address
        A=M+1
        D=D-M  // D = *(cur_address) - *(cur_address+1)

        @j
        M=M+1  // j++

        @SWAP
        D;JLT  // if list[cur_index] < list[cur_index+1], goto SWAP
               // (where cur_address is the address of list[cur_index])

        @INNERLOOP
        0;JMP  // goto INNERLOOP


    @i
    M=M+1 // i++
         
    @OUTTERLOOP
    0;JMP // goto OUTTERLOOP
    

(SWAP)
    @cur_address
    A=M
    D=M
    @temp
    M=D  // temp = list[cur_index]

    @cur_address
    A=M+1
    D=M   
    @cur_address
    A=M
    M=D  // list[cur_index] = list[cur_index+1]

    @temp
    D=M
    @cur_address
    A=M+1
    M=D  // list[cur_index+1] = temp       

    @INNERLOOP
    0;JMP // goto INNERLOOP

(END)
    @END
    0;JMP  // program termination

