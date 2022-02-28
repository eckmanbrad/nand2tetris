// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.


(OUTTERLOOP)
   //* Init params *//
   @SCREEN
   D=A
   @address
   M=D // address = SCREEN

   @8192 // (256*512)/16, the number of 16-bit registers
   D=A   // dedicated to the keyboard memory map
   @n
   M=D // n = 8192

   @i
   M=0 // i = 0

   @black
   M=0 // black = 0 (black indicator bit)

   @KBD
   D=M
   @SETBLACK
   D;JNE // if KBD != 0 goto SETBLACK
   @LOOP
   0;JMP // else keep black bit off, skip to LOOP

   (SETBLACK)
      @black
      M=1 // black = 1 (turns on black indicator bit)

   //* Loop over 16-bit words in memory keyboard map and color appropriately *//
   (LOOP)
      @i
      D=M
      @n
      D=D-M
      @OUTTERLOOP
      D;JEQ // if i==n goto OUTTERLOOP

      @black
      D=M
      @WHITEN
      D;JEQ // if black bit is turned off goto WHITEN
      @BLACKEN
      0;JMP // else goto BLACKEN

      (BLACKEN)
         @address
         A=M
         M=-1 // RAM[address] = 1111111111111111 (black)
         @CONTINUE
         0;JMP // skip whiten instruction

      (WHITEN)
         @address
         A=M
         M=0 // RAM[address] = 0000000000000000 (white)

      (CONTINUE)
      @address
      M=M+1 // address++
       
      @i
      M=M+1 // i++
         
      @LOOP
      0;JMP // goto LOOP
