fn puts(data: str) -> int {
    return syscall write(1, cstr(data), strlen(data));
}

fn exit(code: int) -> void {
    syscall exit(code);
}