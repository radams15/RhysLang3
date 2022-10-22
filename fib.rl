fn fib(a: int) -> int {
    if(a <= 1){
        return 1;
    }

    return fib(a-2) + fib(a-1);
}

fn main() -> int {
    var fibbed = fib(10);
    fibbed = fibbed + 1;

    print(fibbed);

    return 0;
}