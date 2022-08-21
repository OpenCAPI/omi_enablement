#include "functions.h"

int containts(char* list, char c){
    for(int i=0; i<sizeof(list); i++){
        if(tolower(c)==tolower(list[i])) return 1;
    }
    return 0;
}

void print_buf(uint8_t* buf, int size){
    for(int i=0; i<size; i++){
        printf("%x\n", buf[i]);
    }
}

long long bytelist2int(uint8_t* list, int size){
    long long value = 0;
    for(int i=0; i<size; i++){
        value += (long long) list[i] << (8*((size-1)-i));
    }
    return value;
}

uint8_t* int2bytelist(long long value, int size){
    uint8_t* list = (uint8_t*) calloc(size, sizeof(uint8_t));

    for (size_t i = 0; i < size; ++i) {
        unsigned char byte = *((unsigned char *)&value + i);
        list[(size-1)-i] = byte;
    }
    return list;
}
