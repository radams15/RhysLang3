section .text

; Return first byte of the string
strlen:
    push bp
	mov bp, sp

    push bx
    mov bx, dx
    xor ax, ax
    mov al, [bx]
    pop bx

    mov sp, bp
    pop bp
    ret

; inc str by 1 and return
cstr:
    push bp
	mov bp, sp

	push dx
    add dx, 1
    mov ax, dx
    pop dx

    mov sp, bp
    pop bp
    ret