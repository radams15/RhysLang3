section .text

; Return first byte of the string
strlen:
    push ebp
	mov ebp, esp

    xor eax, eax
    mov al, [ebx]

    mov esp, ebp
    pop ebp
    ret

; inc str by 1 and return
cstr:
    push ebp
	mov ebp, esp

	push ebx
    add ebx, 1
    mov eax, ebx
    pop ebx

    mov esp, ebp
    pop ebp
    ret