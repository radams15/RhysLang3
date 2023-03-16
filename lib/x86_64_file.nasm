section .text

; Return first byte of the string
strlen:
    push rbp
	mov rbp, rsp

    xor rax, rax
    mov al, [rdi]

    mov rsp, rbp
    pop rbp
    ret

; inc str by 1 and return
cstr:
    push rbp
	mov rbp, rsp

	push rdi
    add rdi, 1
    mov rax, rdi
    pop rdi

    mov rsp, rbp
    pop rbp
    ret