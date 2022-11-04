# RhysLang

## Attempt 3

---

This is a simple language composed of functions, variables and classes.

Currently compiles to linux x86_64 assembly and has a small standard
library using linux syscalls and c extensions.

## Example program: Fibonacci

``` rust
fn fib(a: int) -> int {
    if(a <= 1){
        return 1;
    }

    return fib(a-2) + fib(a-1);
}

fn main() -> int {
    var fibbed: int = fib(10);

    puts(fibbed);

    return 0;
}
```