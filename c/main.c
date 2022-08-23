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
#include "explorer.h"
#include "components.h"
#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include <getopt.h>

void func(int argc, char *argv[]){
    int file = 0;
    int busnum = 0;
    int opt;
    /* Reading Operation */
    if(strcmp(argv[1], "read") == 0){
        char* pEnd;
        char* component; // fire or explorer/ice
        long long reg;
        while ((opt = getopt(argc, argv, ":b:c:r:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'c':
                component = strdup(optarg);
                break;
            case 'r':
                reg = (long long) strtoll(optarg, &pEnd, 16);
                break;
            }
        }
        if(strcmp(component, "fire") == 0){
            file = fire_i2c_init(busnum);
            fire_read(reg, file);
            printf("%#llx\n", fire_read(reg, file));
        }
        if(strcmp(component, "explorer") == 0){
            file = explorer_i2c_init(busnum);
            explorer_double_read(reg, file);
            printf("%#llx\n", explorer_double_read(reg, file));
        }
    }

    /* Writing Operation */
    if(strcmp(argv[1], "write") == 0){
        char* pEnd;
        char* component; // fire or explorer/ice
        long long reg, data;
        int res;
        while ((opt = getopt(argc, argv, ":b:c:r:d:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'c':
                component = strdup(optarg);
                break;
            case 'r':
                reg = (long long) strtoll(optarg, &pEnd, 16);
                break;
            case 'd':
                data = (long long) strtoll(optarg, &pEnd, 16);
                break;
            }
        }
        if(strcmp(component, "fire") == 0){
            file = fire_i2c_init(busnum);
            res = fire_write(reg, data, file);
            printf("Writing check: %s\n", res ? "Success" : "Failed");

        }
        if(strcmp(component, "explorer") == 0){
            file = explorer_i2c_init(busnum);
            res = explorer_double_write(reg, data, file);
            printf("Writing check: %s\n", res ? "Success" : "Failed");
        }
    }

    /* DDIMM reset Operation */
    if(strcmp(argv[1], "ddimmreset") == 0){
        char *ddimms, *state;
        while ((opt = getopt(argc, argv, ":b:d:s:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'd':
                ddimms = strdup(optarg);
                break;
            case 's':
                state = strdup(optarg);
                break;
            }
        }
        file = fire_i2c_init(busnum);
        if(strcmp(state, "on") == 0) set_ddimm_on_reset(file, ddimms);
        if(strcmp(state, "off") == 0) set_ddimm_off_reset(file, ddimms);
    }

    /* Explorer sync init */
    if(strcmp(argv[1], "init") == 0) {
        sleep(2);
        while ((opt = getopt(argc, argv, ":b:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            }
        }
        file = explorer_i2c_init(busnum);
        explorer_init(file, 333);
    }

    /* Sync */
    if(strcmp(argv[1], "sync") == 0){
        char *ddimms;
        while ((opt = getopt(argc, argv, ":b:d:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'd':
                ddimms = strdup(optarg);
                break;
            }
        }
        int explorer_file = explorer_i2c_init(busnum);
        explorer_sync(explorer_file, 333);
        sleep(1);
        int fire_file = fire_i2c_init(busnum);
        fire_sync(fire_file, ddimms);
        sleep(4);
        explorer_check_sync(explorer_file);

    }

    /* Check sync from FIRE */
    /* Sync */
    if(strcmp(argv[1], "checksync") == 0){
        char *ddimms;
        while ((opt = getopt(argc, argv, ":b:d:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'd':
                ddimms = strdup(optarg);
                break;
            }
        }
        file = fire_i2c_init(busnum);
        fire_check_sync(file, ddimms);

    }

    /* Get info */
    if(strcmp(argv[1], "info") == 0){
        char* component; // fire or explorer/ice
        while ((opt = getopt(argc, argv, ":b:c:")) != -1){
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'c':
                component = strdup(optarg);
                break;
            }
        }
        if(strcmp(component, "explorer") == 0){
            file = explorer_i2c_init(busnum);
            explorer_init(file, 333);
            explorer_get_firmware_info(file);
        }
        if(strcmp(component, "fire") == 0){
            file = fire_i2c_init(busnum);
            long long id = get_fire_id(file);
            long long is_dirty = (id & (1 << 28)) >> 28;
            printf("ID : %#llx | Is Dirty? %s\n", id, (is_dirty) ? "Yes" : "No");
        }
    }

    /* Get path */
    if(strcmp(argv[1], "initpath") == 0){
    	printf("Setting up ddimms:\n");
        char *ddimms;
        while ((opt = getopt(argc, argv, ":b:d:")) != -1) {
            switch (opt)
            {
            case 'b':
                busnum = atoi(optarg);
                break;
            case 'd':
                ddimms = strdup(optarg);
                break;
            }
        }
        setup_ddimm_path(busnum, ddimms);
    }
}

int main(int argc, char *argv[])
{
    func(argc, argv);

    // setup_ddimm_path(0, "a");
    // int file;
    // file = pmic_i2c_init(PMIC1_I2C_ADDR, 3);
    // pmic_write(PMIC1_I2C_ADDR, 0x80, file);
    // file = pmic_i2c_init(PMIC2_I2C_ADDR, 3);
    // pmic_write(PMIC2_I2C_ADDR, 0x80, file);
    // printf("%#x\n", pmic_read(file));


    return 0;
}
