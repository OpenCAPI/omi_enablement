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
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include "smbus.h"
#include <unistd.h>
#include "functions.h"

#define MUX1_I2C_ADDR  0x70
#define MUX2_I2C_ADDR  0x73
#define MUX3_I2C_ADDR  0x71

#define PMIC1_I2C_ADDR 0x4f
#define PMIC2_I2C_ADDR 0x67

#define DDIMMA  0
#define DDIMMB  1

#define EEPROM_I2C_ADDR 0x50
#define POWER_CTRL_I2C_ADDR 0x64
#define I2C_ADDR_RANGE 127

// ------------- MUX ---------------- //
int mux_i2c_init(int muxaddr, int busnum);
uint8_t mux_read(int file);
void mux_write(uint8_t muxaddr, uint8_t data, int file);

// ------------- PMIC --------------- //
int pmic_i2c_init(int pmicaddr, int busnum);
uint8_t pmic_read(int file);
void pmic_write(uint8_t pmicaddr, uint8_t data, int file);
void open_path(int busnum);
void close_path(int busnum);
void set_pmics(int busnum);
void clear_pmics(int busnum);
void setup_ddimm_path(int busnum, char* ddimms);
