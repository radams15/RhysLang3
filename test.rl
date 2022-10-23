fn main() -> int {
    var out: int = 0;

    for(var i: int=1 ; i<=10 ; i = i+1){
        if(i == 1){
            out = out + 100;
        }else{
            out = out + i;
        }
    }

    return out;
}