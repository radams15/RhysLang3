fn puts(data: str) -> int {
    return syscall 1(1, data, strlen(data)+1);
}