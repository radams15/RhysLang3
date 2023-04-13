_malloc_counter: dd 0xa000

malloc:
	push bp
	mov bp, sp

    sub [_malloc_counter], dx
    lea ax, _malloc_counter

    mov sp, bp
    pop bp
    ret