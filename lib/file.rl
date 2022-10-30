struct File {
    fd: int;

    fn write(to_write: str) -> int {
        var len: int = strlen(to_write);

        return syscall write(this.fd, to_write, len);
    }

    fn close() -> int {
        return syscall close(this.fd);
    }
}

fn fopen(name: str, mode: char) -> File {
    var modecode: int = 100;
    if(mode == 'r'){
        modecode = modecode | 0;
    } else if(mode == 'w'){
        modecode = modecode | 2;
    }

    var fd: int = syscall open(name, modecode, 777);

    var out: File = alloc File;

    out.fd = fd;

    return out;
}