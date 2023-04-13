
struct List {
    items: ptr;
    length: int;

    static fn new() -> List {
        cif (linux) {
            var this: List = alloc List;

            this.length = 0;
            this.items = alloc int;

            return this;
        } else {
            return 0;
        }
    }

    fn at(i: int) -> ptr;
    fn append(item: ptr) -> void;
}
