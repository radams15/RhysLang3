fn sub(a: int, b: int) -> int {
    return a-b;
}

fn clock() -> int;
fn printi(a: int) -> int;
fn puts(a: str) -> void;
fn printf(a: str, b: str) -> void;

fn exponent(a: int, exp: int) -> int {
    var out: int = a;

    for(var i: int=0 ; i<exp-1 ; i = i + 1){
        out = out * a;
    }

    return out;
}

fn fib(a: int) -> int {
    if(a <= 2){
        return 1;
    }

    return fib(sub(a, 2)) + fib(sub(a, 1));
}

fn main() -> int {
    var out: int = exponent(5, 2);

    var name: str = "rhys";
    printf("hello world %s %d\n\n", name, 5);

    return out;
}