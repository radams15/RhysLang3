global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!";

fn main() -> int {
    var fd: int = fopen(file_name, 'w');

    fwrite(fd, to_write);

    fclose(fd);

    puts("Done!\n");

    return 1;
}