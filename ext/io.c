#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*int strlen(char* inp) {
    int out=0;

    while(*inp != '\0'){
        out++;
        inp++;
    }

    return out;
}*/

int writei(int i){
    printf("%d\n", i);

    return 0;
}

char* add_str(char* a, char* b){
    char* out = calloc(strlen(a)+strlen(b)+1, sizeof(char));

    strcpy(out, a);
    strcat(out, b);

    return out;
}