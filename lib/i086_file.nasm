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


; fopen(name: str)
fopen:
    push bp
	mov bp, sp

    call cstr
    mov dx, ax

    mov cx, 0 ; no. bytes to write to new file.

    mov ah, 0x3c
    mov al, 0x2
    int 0x21

    jc err

    mov sp, bp
    pop bp
    ret

err:
    mov dx, ErrorOpenMsg
    mov ah, 0x9
    int 0x21
    ret


FName: db 'out.txt', 0
ErrorOpenMsg: db 'Error opening!', '$'