#include <stdio.h>
#include <string.h>
#include <stdlib.h>

struct String {
    char* val;
};

struct String* String___add(struct String* this, char* end){
    char* out_str = calloc(strlen(this->val)+strlen(end)+1, sizeof(char));

    sprintf(out_str, "%s%s", this->val, end);

    struct String* out = malloc(sizeof(struct String));
    out->val = out_str;

    return out;
}

int String___length(struct String* this) {
    int out = 0;

    char* inp = this->val;

    while(*inp != '\0'){
        out++;
        inp++;
    }

    return out;
}

char String___at(struct String* this, int i){
    return this->val[i];
}