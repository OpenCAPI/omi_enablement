#include "functions.h"

opyright 2022 International Business Machines
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# The patent license granted to you in Section 3 of the License, as applied
# to the "Work," hereby includes implementations of the Work in physical form.
#
# Unless required by applicable law or agreed to in writing, the reference design
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.
#
# The background Specification upon which this is based is managed by and available from
# the OpenCAPI Consortium.  More information can be found at https://opencapi.org.
#

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
