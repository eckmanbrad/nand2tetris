// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
//
// This program only needs to handle arguments that satisfy
// R0 >= 0, R1 >= 0, and R0*R1 < 32768.

   //* Init params *//
   @R2
   M=0 // RAM[2] = 0

   @R0
   D=M
   @base  // number to continually add
   M=D // base = RAM[0]

   @R1
   D=M
   @n  // number of iterations to add
   M=D // n = RAM[1]

   @prod  // the product being computed
   M=0 // prod = 0

   @i  // loop counter
   M=0 // i = 0

//* Add base to itself n times *//
(LOOP)
   @i
   D=M
   @n
   D=D-M
   @STORE
   D;JEQ // if i==n goto STORE

   @base
   D=M
   @prod
   M=D+M // prod = prod + base

   @i
   M=M+1 // i++

   @LOOP
   0;JMP // goto LOOP

//* Store product in specified RAM address *//
(STORE)
   @prod
   D=M
   @R2
   M=D // RAM[2] = prod

(END)
   @END
   0;JMP // program termination
   
   
   

   
   



   


