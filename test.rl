global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!\n\n";
global done_str: str = "Done!\n";

/*struct Person {
    name: str;
    age: int;
}*/

fn main() -> int {
    var fd: int = fopen(file_name, 'w');

    fwrite(fd, to_write);

    fclose(fd);

    return 1;
}