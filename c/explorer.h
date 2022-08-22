#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include "smbus.h"
#include <unistd.h>
#include "functions.h"

// General attributes
#define EXP_I2C_ADDR                   0x20
#define EXP_ADDR_OFFSET                0xA0000000
#define EXP_TRAINING_DONE   (1ULL << 39)
#define EXP_ID_NUM_REG    0x02090000

// Register EXP_FW_REGISTERS[]  = {EXP_REG_NUM_IMAGES, EXP_REG_PARTITION_ID, EXP_REG_MAJOR_A, EXP_REG_MINOR_A, EXP_REG_BUILD_PATCH_A, EXP_REG_BUILD_NUMBER_A, EXP_REG_BUILD_DATE_A,
//                     EXP_REG_MAJOR_B, EXP_REG_MINOR_B, EXP_REG_BUILD_PATCH_B, EXP_REG_BUILD_NUMBER_B, EXP_REG_BUILD_DATE_B, EXP_REG_RAM_SIZE_IN_BYTES,
//                     EXP_REG_CHIP_VERSION, EXP_REG_SPI_FLASH_ID, EXP_REG_SPI_FLASH_SECTOR_SIZE, EXP_REG_SPI_FLASH_SIZE, EXP_REG_ERROR_BUFFER_SIZE, EXP_REG_IMAGE_INDEX};

// Training and errors

// Error EXP_ERRORS[] = {EXP_DL0_CERR_00, EXP_DL0_CERR_01, EXP_DL0_CERR_02, EXP_DL0_CERR_03, EXP_DL0_CERR_04, EXP_DL0_CERR_05, EXP_DL0_CERR_06, EXP_DL0_CERR_07,
//             EXP_DL0_CERR_08, EXP_DL0_CERR_09, EXP_DL0_CERR_10, EXP_DL0_CERR_11, EXP_DL0_CERR_12, EXP_DL0_CERR_13, EXP_DL0_CERR_14, EXP_DL0_CERR_15,
//             EXP_DL0_CERR_16, EXP_DL0_CERR_17, EXP_DL0_CERR_18, EXP_DL0_CERR_19, EXP_DL0_CERR_20, EXP_DL0_CERR_21, EXP_DL0_CERR_22, EXP_DL0_CERR_23,
//             EXP_DL0_CERR_24, EXP_DL0_CERR_25, EXP_DL0_CERR_26, EXP_DL0_CERR_27, EXP_DL0_CERR_28, EXP_DL0_CERR_29, EXP_DL0_CERR_30, EXP_DL0_CERR_31,
//             EXP_DL0_CERR_32, EXP_DL0_CERR_33, EXP_DL0_CERR_34, EXP_DL0_CERR_35, EXP_DL0_CERR_36, EXP_DL0_CERR_37, EXP_DL0_CERR_38, EXP_DL0_CERR_39,
//             EXP_DL0_CERR_40, EXP_DL0_CERR_41, EXP_DL0_CERR_42, EXP_DL0_CERR_43, EXP_DL0_CERR_44, EXP_DL0_CERR_45, EXP_DL0_CERR_46, EXP_DL0_CERR_47};


int explorer_i2c_init(int busnum);
void explorer_get_firmware_info(int file);
long long explorer_simple_read(uint8_t reg, int file);
void explorer_simple_write(long long reg, uint8_t reg_type, uint8_t size, int file);
long long explorer_double_read(long long reg_addr, int file);
int explorer_double_write(long long reg_addr, long long data, int file);
void explorer_init(int file, int freq);
void explorer_sync(int file, int freq);
void explorer_check_sync(int file);
