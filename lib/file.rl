struct File {
    fd: int;

    fn write(to_write: str) -> int {
        return syscall write(this.fd, cstr(to_write), strlen(to_write));
    }

    fn close() -> int {
        return syscall close(this.fd);
    }

    static fn open(name: str, mode: char) -> File {
        cif(linux) {
            var modecode: int = 100;
            if(mode == 'r'){
                modecode |= 0;
            } else if(mode == 'w'){
                modecode |= 2;
            }

            var fd: int = syscall open(cstr(name), modecode, 777);

            var out: File = alloc File;

            out.fd = fd;

            return out;
        } else {
            var out: File = alloc File;
            return out;
        }
    }
}