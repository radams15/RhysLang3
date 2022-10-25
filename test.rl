fn sub(a: int, b: int) -> int {
    return a-b;
}

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
    var file_name: str = "out.txt";

    var fd: int = fopen(file_name, 'w');

    fwrite(fd, "a\n\n");

    fclose(fd);

    return 1;
}