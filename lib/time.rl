
struct TimeVal{
    sec: int;
    usec: int;
}

fn timeofday() -> TimeVal {
    var out: TimeVal = alloc TimeVal;

    syscall gettimeofday(out, 0);

    return out;
}

fn time() -> int {
    var timeofday: TimeVal = timeofday();

    var out: int = timeofday.sec;
    free(timeofday);

    return out;
}