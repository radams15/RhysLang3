#include <stdio.h>
#include <stdlib.h>

struct List {
    void** items;
    int length;
};

void* List___at(struct List* this, int i){
    if(i > this->length-1){
        // Invalid index

        fprintf(stderr, "Cannot get list item at index %d!\n", i);

        exit(1);
    }

    return this->items[i];
}

void List___append(struct List* this, void* item){
    this->length++;
    this->items = realloc(this->items, this->length*sizeof(int));

    this->items[this->length-1] = item;
}