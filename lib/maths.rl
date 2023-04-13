fn pow(a: int, exp: int) -> int {
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

    return fib(a-2) + fib(1-2);
}
