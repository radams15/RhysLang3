fn puts(data: str) -> int {
    var len: int = strlen(data);
    var c_str: ptr = cstr(data);

    cif (dos) {
        return syscall puts(c_str);
    } else {
        return syscall write(1, c_str, len);
    }
}

fn putc(char: int) -> int {
    cif (dos) {
        return syscall putc(char);
    } else {
        return syscall write(1, int, 1);
    }
}

fn puti(i: int) -> int { // TODO: is broken as no modulo
    var base: int = 10;

    while (i != 0) {
        /*var char: int = i % base;
        putc(char + 48);*/
        i /= base;
    }

    return 0;
}

fn exit(code: int) -> void {
    syscall exit(code);
}