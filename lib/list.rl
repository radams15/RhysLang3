
struct List {
    items: ptr;
    length: int;

    /*static fn new() -> List {
        var this: List = alloc List;

        this.length = 0;
        this.items = alloc int;

        return this;
    }*/

    fn at(i: int) -> ptr;
    fn append(item: ptr) -> void;
}
