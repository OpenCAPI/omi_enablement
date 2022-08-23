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

#define FIRE_I2C_ADDR 0x38
#define FIRE_FML_REG_BASE_ADDR  0x0100000000000000
#define FIRE_C3S_REG_BASE_ADDR  0x0101000000000000
#define FIRE_FBIST_REG_BASE_ADDR  0x0102000000000000

#define FIRE_FML_FIRE_VERSION_REG     FIRE_FML_REG_BASE_ADDR + 0x00
#define FIRE_FML_RESET_CONTROL_REG     FIRE_FML_REG_BASE_ADDR + 0x04
#define FIRE_FML_LED_CONTROL_REG     FIRE_FML_REG_BASE_ADDR + 0x08
#define FIRE_FML_LED_OVERRIDE_REG     FIRE_FML_REG_BASE_ADDR + 0x0c

#define FIRE_FML_DDMIMM_DETECT_REG    FIRE_FML_REG_BASE_ADDR + 0x20

#define FIRE_FML_DDIMMA_RESET_BIT     (1 << 3)
#define FIRE_FML_DDIMMB_RESET_BIT     (1 << 2)
#define FIRE_FML_DDIMMC_RESET_BIT     (1 << 1)
#define FIRE_FML_DDIMMD_RESET_BIT     (1 << 0)
#define FIRE_FML_DDIMMW_RESET_BIT     (1 << 4)

#define FIRE_ID_DIRTY_BIT  (1 << 28)

#define FIRE_FML_LED_DDIMMW_RED_OVERRIDE_EN  (1 << 17)
#define FIRE_FML_LED_DDIMMW_GREEN_OVERRIDE_EN  (1 << 16)
#define FIRE_FML_LED_DDIMMA_RED_OVERRIDE_EN  (1 << 13)
#define FIRE_FML_LED_DDIMMA_GREEN_OVERRIDE_EN  (1 << 12)
#define FIRE_FML_LED_DDIMMB_RED_OVERRIDE_EN  (1 << 9)
#define FIRE_FML_LED_DDIMMB_GREEN_OVERRIDE_EN  (1 << 8)
#define FIRE_FML_LED_DDIMMC_RED_OVERRIDE_EN  (1 << 5)
#define FIRE_FML_LED_DDIMMC_GREEN_OVERRIDE_EN  (1 << 4)
#define FIRE_FML_LED_DDIMMD_RED_OVERRIDE_EN  (1 << 1)
#define FIRE_FML_LED_DDIMMD_GREEN_OVERRIDE_EN  (1 << 0)

#define I2C_REG_NOT_FOUND_READ_ERROR  0xDEC0DE1C

/*--------------- C3S --------------*/
#define C3S_OFFSET                         0x0101000000000000
#define REG_C3S_RESP_CNTL                  0x00030004
#define REG_C3S_CNTL                       0x00030000
#define FIELD_C3S_RESP_WRITE_ADDR_RESET    9
#define FIELD_C3S_START                    0
#define FIELD_C3S_DONE                     3
#define FIELD_C3S_STOP                     1

/*-------------- Config Host ---------------*/

#define FIRE_DDIMMA_HOST_CONF_BASE_ADDR  0x0104000000000000
#define FIRE_DDIMMB_HOST_CONF_BASE_ADDR  0x0104040000000000
#define FIRE_DDIMMC_HOST_CONF_BASE_ADDR  0x0104080000000000
#define FIRE_DDIMMD_HOST_CONF_BASE_ADDR  0x01040C0000000000

#define FIRE_DDIMMA_OPENCAPI_DL_CONTROL  FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10
#define FIRE_DDIMMB_OPENCAPI_DL_CONTROL  FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10

#define FIRE_DDIMMA_HOST_CONF_STATUS_REG  FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x20
#define FIRE_DDIMMB_HOST_CONF_STATUS_REG  FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x20

#define DDIMM_HOST_CONF_UP_BIT  (1 << 3)

int fire_i2c_init(int busnum);
long long fire_read(long long reg, int file);
int fire_write(long long reg, long long data, int file);
long long get_fire_id(int file);
void set_ddimm_on_reset(int file, char* ddimms);
void set_ddimm_off_reset(int file, char* ddimms);
void fire_sync(int file, char* ddimms);
void fire_check_sync(int file, char* ddimms);
