#define NULL ((void*) 0)

int strlen(char* inp){
    int out=0;

    while(*inp != '\0'){
        out++;
        inp++;
    }

    return out;
}