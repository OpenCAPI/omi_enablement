#
# Copyright 2022 International Business Machines
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
#include "fire.h"

/*
    Initialize the i2c bus and scan for FIRE's address
*/
int fire_i2c_init(int busnum){
    /* Getting the i2c bus number */
    char filename[20];
    int file, res;
    snprintf(filename, 19, "/dev/i2c-%d", busnum);

    /* Testing the i2c bus device */
    file = open(filename, O_RDWR);
    if (file < 0) exit(1);
    if (ioctl(file, I2C_SLAVE, FIRE_I2C_ADDR) < 0) exit(1);

    /* Scanning the i2c bus for FIRE's address */
    res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE);
    if (res < 0){
        printf("FIRE i2c address is not detected.\n");
        exit(1);
    }
    return file;
}

/*
    Read a Fire's register value.
    The operation will write a 8 bytes value representing the register address to read its value,
    followed by 8 reads of 1 byte each that form the register content.
    Both the I2C operations are done without providing any register address.
    The hardware automatically puts the result in a FIFO tied directly to I2C bus.
*/
long long fire_read(long long reg, int file){
    uint8_t command[8] = {0}; // command array, needs to be declared static
    uint8_t* buf;             // return value
    uint8_t* reg_list;        // register address as array

    /* Preparing the command content */
    reg_list = int2bytelist(reg, 8);
    for(int i=0; i<8; i++) command[i] = reg_list[i];

    /* Sending the i2c commad */
    struct i2c_msg message = { FIRE_I2C_ADDR, 0, sizeof(command), command};
    struct i2c_rdwr_ioctl_data ioctl_data = { &message, 1 };
    ioctl(file, I2C_RDWR, &ioctl_data);

    /* Getting the register's data */
    buf = (uint8_t*) calloc(8, 8);
    for(int i=0; i<8; i++) read(file, &buf[i], 1);

    return bytelist2int(buf, 8);
}

/*
    Write data in a Fire's register.
    The operation will write a 16 bytes value representing the register address
    to modify its value (8 bytes) + the data to write (8 bytes).
    It also checks if the write operation has succeeded or not.
*/
int fire_write(long long reg, long long data, int file){
    uint8_t command[16];     // command array, needs to be declared static (concat of both reg address and data arrays)
    long long new_value;     // used to check writing success
    uint8_t* reg_list;       // register address as array
    uint8_t* data_list;      // data to put in register as array

    /* Preparing the command content */
    reg_list = int2bytelist(reg, 8);
    data_list = int2bytelist(data, 8);
    for(int i=0; i<8; i++){
        command[i] = reg_list[i];
        command[i+8] = data_list[i];
    }

    /* Sending the i2c commad */
    struct i2c_msg message = { FIRE_I2C_ADDR, 0, sizeof(command), command };
    struct i2c_rdwr_ioctl_data ioctl_data = { &message, 1 };
    ioctl(file, I2C_RDWR, &ioctl_data);

    /* Checking */
    fire_read(reg, file); // flush out the buffer
    new_value = fire_read(reg, file);
    return (new_value == data);
}

/*  Get the ID of FIRE and check the Dirty bit.
    It's the operation of reading the content value of FIRE_FML_FIRE_VERSION_REG register.
*/
long long get_fire_id(int file){
    return fire_read(FIRE_FML_FIRE_VERSION_REG, file);
}

/*
    Make provided DDIMM(s) enter Reset State.
    RESET STATE = ON
*/
void set_ddimm_on_reset(int file, char* ddimms){
    long long val = fire_read(FIRE_FML_RESET_CONTROL_REG, file);
    if (containts(ddimms, 'a')) val = val & ~FIRE_FML_DDIMMA_RESET_BIT;
    if (containts(ddimms, 'b')) val = val & ~FIRE_FML_DDIMMB_RESET_BIT;
    if (containts(ddimms, 'c')) val = val & ~FIRE_FML_DDIMMC_RESET_BIT;
    if (containts(ddimms, 'd')) val = val & ~FIRE_FML_DDIMMD_RESET_BIT;
    if (containts(ddimms, 'w')) val = val & ~FIRE_FML_DDIMMW_RESET_BIT;
    fire_write(FIRE_FML_RESET_CONTROL_REG, val, file);
}

/*
    Make provided DDIMM(s) exist Reset State.
    RESET STATE = OFF
*/
void set_ddimm_off_reset(int file, char* ddimms){
    long long val = fire_read(FIRE_FML_RESET_CONTROL_REG, file);
    if (containts(ddimms, 'a')) val = val | FIRE_FML_DDIMMA_RESET_BIT;
    if (containts(ddimms, 'b')) val = val | FIRE_FML_DDIMMB_RESET_BIT;
    if (containts(ddimms, 'c')) val = val | FIRE_FML_DDIMMC_RESET_BIT;
    if (containts(ddimms, 'd')) val = val | FIRE_FML_DDIMMD_RESET_BIT;
    if (containts(ddimms, 'w')) val = val | FIRE_FML_DDIMMW_RESET_BIT;
    fire_write(FIRE_FML_RESET_CONTROL_REG, val, file);
}

void fire_sync(int file, char* ddimms){
    if (containts(ddimms, 'a')){
        fire_read(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, file);
        fire_write(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045, file);
        fire_write(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045, file);
    }
    if (containts(ddimms, 'b')){
        fire_read(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, file);
        fire_write(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045, file);
        fire_write(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045, file);
    }
}

void fire_check_sync(int file, char* ddimms){
    long long reg, res;
    for(int i=0; i<sizeof(ddimms); i++){
        if (ddimms[i] == 0) break;
        if(containts(ddimms, 'a')) reg = FIRE_DDIMMA_HOST_CONF_STATUS_REG;
        else if(containts(ddimms, 'b')) reg = FIRE_DDIMMB_HOST_CONF_STATUS_REG;
        fire_read(reg, file);
        res= fire_read(reg, file);

        if (res & (1 << 3)){
            printf("DDIMM%c is in sync\n", ddimms[i]);
        }
        else
            printf("DDIMM%c is NOT in sync\n", ddimms[i]);
    }

}
