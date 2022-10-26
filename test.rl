global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!\n\n";
global done_str: str = "Done!\n";

fn main() -> int {
    var fd: int = fopen(file_name, 'w');

    fwrite(fd, to_write);

    fclose(fd);

    puts(done_str);

    return 1;
}