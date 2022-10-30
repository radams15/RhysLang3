global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!\n\n";
global done_str: str = "Done!\n";

struct Person {
    profession: str,
    name: str,
    age: int
}

fn main() -> int {
    var jeff: Person = 0;

    jeff.name = "Jeff";

    syscall write(1, jeff.name, 29);

    /*var fd: int = fopen(file_name, 'w');

    fwrite(fd, jeff.name);

    fclose(fd);

    return 1;*/
}