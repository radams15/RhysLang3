fn fopen(name: str, mode: char) -> int {
    var modecode: int = 100;
    if(mode == 'r'){
        modecode = modecode | 0;
    } else if(mode == 'w'){
        modecode = modecode | 2;
    }

    return syscall 2(name, modecode);
}

fn fwrite(fd: int, to_write: str) -> int {
    var len: int = strlen(to_write);

    return syscall 1(fd, to_write, len);
}

fn fclose(fd: int, to_write: str) -> int {
    return syscall 3(fd);
}