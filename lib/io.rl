fn puts(data: str) -> int {
    return syscall write(1, data, strlen(data)+1);
}

fn exit(code: int) -> void {
    syscall exit(code);
}