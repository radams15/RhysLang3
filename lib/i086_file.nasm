section .text

; Return first byte of the string
strlen:
    push bp
	mov bp, sp

    xor ax, ax
    mov al, [bx]

    mov sp, bp
    pop bp
    ret

; inc str by 1 and return
cstr:
    push bp
	mov bp, sp

	push bx
    add bx, 1
    mov ax, bx
    pop bx

    mov sp, bp
    pop bp
    ret