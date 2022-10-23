global exponent
extern pow

exponent:
        mov rax, 1
        ret

global _start
_start:
	call main

	mov rdi, rax
	mov rax, 60
	syscall