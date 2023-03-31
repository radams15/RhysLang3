global to_write: str = "hello world!\n";
global to_write2: str = "howdy earth!";

fn main() -> int {
    puts(to_write);
    puts(to_write2);

    return 1;
}