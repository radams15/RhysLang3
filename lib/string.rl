fn strlen(string: str) -> int;

struct String {
    val: str;

    static fn new(val: str) -> String {
        var this: String = alloc String;

        this.val = val;

        return this;
    }

    fn add(end: str) -> String;
    fn length() -> int;
    fn at(i: int) -> char;

    fn cstr() -> str {
        return this.val;
    }
}