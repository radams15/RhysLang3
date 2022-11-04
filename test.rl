global file_name: str = "out.txt";
global to_write: str = "hello world: this is text!\n\n";
global done_str: str = "Done!\n";

/*struct Person {
    profession: str;
    name: str;
    age: int;

    static fn new(name: str, age: int) -> Person {
        var this: Person = alloc Person;
        this.name = name;
        this.age = age;

        return this;
    }

    fn ageafter(years: int) -> int {
        return this.age + years;
    }
}*/

fn main() -> int {
    var name: String = String.new("Alan");
    name = name.add("\n");
    puts(name.cstr());
    writei(name.length());
    writei(name.at(0));

    /*var to_add: int = 5;
    var jeff: Person = Person.new("Jeff", 10);

    var time: int;
    for(var i: int=0 ; i<5 ; i += 1) {
        time = time();
        writei(time); // Print the time to console
    }

    var file: File = File.open(file_name, 'w');

    writei(jeff.age);

    file.write(str_add(jeff.name, "\nBye\n\n"));

    file.close();

    free(jeff);
    free(file);*/

    return 1;
}