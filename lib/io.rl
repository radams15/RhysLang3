fn puts(data: str) -> int {
    var len: int = strlen(data);
    var c_str: ptr = cstr(data);

    return syscall write(1, c_str, len);
}

fn exit(code: int) -> void {
    syscall exit(code);
}