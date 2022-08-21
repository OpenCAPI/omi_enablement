#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>

int containts(char* list, char c);
void print_buf(uint8_t* buf, int size);
long long bytelist2int(uint8_t* list, int size);
uint8_t* int2bytelist(long long value, int size);
