global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!\n\n";
global done_str: str = "Done!\n";

struct Person {
    profession: str;
    name: str;
    age: int;

    fn ageafter(years: int) -> int {
        return this.age + years;
    }
}

fn main() -> int {
    var to_add: int = 5;
    var jeff: Person = alloc Person;

    jeff.name = "Jeff\n";
    jeff.age = 10;

    writei(10);

    var file: File = fopen(file_name, 'w');

    file.write(jeff.name);

    file.close();

    return 1;
}