fn sub(a: int, b: int) -> int {
    return a-b;
}

fn fib(a: int) -> int {
    if(a <= 2){
        return 1;
    }

    return fib(sub(a, 2)) + fib(sub(a, 1));
}

fn main() -> int {
    var out: int = fib(11);

    return out;
}