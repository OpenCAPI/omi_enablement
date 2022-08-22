#include "explorer.h"

typedef struct Register{
  long long addr;
  char* label;
}Register;

typedef struct Error{
  int bit;
  char* label;
}Error;


// Firmware registers
Register EXP_REG_NUM_IMAGES         =    {0x102FF00 + EXP_ADDR_OFFSET, "FW number of images"};
Register EXP_REG_PARTITION_ID       =    {0x102FF04 + EXP_ADDR_OFFSET, "Partition ID"};

Register EXP_REG_MAJOR_A            =    {0x102FF08 + EXP_ADDR_OFFSET, "Major (Boot Partion A)"};
Register EXP_REG_MINOR_A            =    {0x102FF0C + EXP_ADDR_OFFSET, "Minor (Boot Partion A)"};
Register EXP_REG_BUILD_PATCH_A      =    {0x102FF10 + EXP_ADDR_OFFSET, "Build patch (Boot Partion A)"};
Register EXP_REG_BUILD_NUMBER_A     =    {0x102FF14 + EXP_ADDR_OFFSET, "Build number (Boot Partion A)"};
Register EXP_REG_BUILD_DATE_A       =    {0x102FF18 + EXP_ADDR_OFFSET, "Build date (Boot Partion A)"};

Register EXP_REG_MAJOR_B            =    {0x102FF1C + EXP_ADDR_OFFSET, "Major (Boot Partion B)"};
Register EXP_REG_MINOR_B            =    {0x102FF20 + EXP_ADDR_OFFSET, "Minor (Boot Partion B)"};
Register EXP_REG_BUILD_PATCH_B      =    {0x102FF24 + EXP_ADDR_OFFSET, "Build patch (Boot Partion B)"};
Register EXP_REG_BUILD_NUMBER_B     =    {0x102FF28 + EXP_ADDR_OFFSET, "Build number (Boot Partion B)"};
Register EXP_REG_BUILD_DATE_B       =    {0x102FF2C + EXP_ADDR_OFFSET, "Build date (Boot Partion B)"};

Register EXP_REG_RAM_SIZE_IN_BYTES  =   {0x102FF30 + EXP_ADDR_OFFSET, "RAM size (in bytes)"};
Register EXP_REG_CHIP_VERSION       =   {0x102FF34 + EXP_ADDR_OFFSET, "Chip version"};
Register EXP_REG_SPI_FLASH_ID       =   {0x102FF38 + EXP_ADDR_OFFSET, "SPI flash ID"};
Register EXP_REG_SPI_FLASH_SECTOR_SIZE= {0x102FF3C + EXP_ADDR_OFFSET, "SPI flash sector size"};
Register EXP_REG_SPI_FLASH_SIZE     =   {0x102FF40 + EXP_ADDR_OFFSET, "SPI flash size"};
Register EXP_REG_ERROR_BUFFER_SIZE  =   {0x102FF44 + EXP_ADDR_OFFSET, "Error buffer size"};
Register EXP_REG_IMAGE_INDEX        =   {0x102FF48 + EXP_ADDR_OFFSET, "Image index"};

Register* EXP_FW_REGISTERS = NULL;


Error EXP_DL0_CERR_00  = {0, "UE on control flit frame buffer"};
Error EXP_DL0_CERR_01  = {1, "UE on control flit replay buffer"};
Error EXP_DL0_CERR_02  = {2, "Ack pointer overflow"};
Error EXP_DL0_CERR_03  = {3, "Illegal run length from TL"};

Error EXP_DL0_CERR_04  = {4, "Truncated flit from TL"};
Error EXP_DL0_CERR_05  = {5, "Data parity error"};
Error EXP_DL0_CERR_06  = {6, "Control parity error"};
Error EXP_DL0_CERR_07  = {7, "RX receiving illegal run length"};
Error EXP_DL0_CERR_08  = {8, "RX receiving slow"};
Error EXP_DL0_CERR_09  = {9, "Illegal Tx Lane reversal request"};
Error EXP_DL0_CERR_10  = {10, "Flit Hammer. Detected a possible DI and brought the link down to prevent the potential data corruption"};
Error EXP_DL0_CERR_11  = {11, "Spare"};
Error EXP_DL0_CERR_12  = {12, "ECC UE on data flit frame buffer"};
Error EXP_DL0_CERR_13  = {13, "ECC UE on data flit replay buffer"};

Error EXP_DL0_CERR_14  = {14, "ECC CE error frame buffer"};
Error EXP_DL0_CERR_15  = {15, "ECC CE error replay buffer"};
Error EXP_DL0_CERR_16  = {16, "CRC error detected"};
Error EXP_DL0_CERR_17  = {17, "NACK received"};
Error EXP_DL0_CERR_18  = {18, "TX side in x4 mode"};
Error EXP_DL0_CERR_19  = {19, "RX side in x4 mode"};
Error EXP_DL0_CERR_20  = {20, "EDPL parity error on lane"};
Error EXP_DL0_CERR_21  = {21, "EDPL parity error on lane"};
Error EXP_DL0_CERR_22  = {22, "EDPL parity error on lane"};
Error EXP_DL0_CERR_23  = {23, "EDPL parity error on lane"};

Error EXP_DL0_CERR_24  = {24, "EDPL parity error on lane"};
Error EXP_DL0_CERR_25  = {25, "EDPL parity error on lane"};
Error EXP_DL0_CERR_26  = {26, "EDPL parity error on lane"};
Error EXP_DL0_CERR_27  = {27, "EDPL parity error on lane"};
Error EXP_DL0_CERR_28  = {28, "Spare"};
Error EXP_DL0_CERR_29  = {29, "Tx_Flit macro detected a reason to retrain the link. Look at CYA Error for details"};
Error EXP_DL0_CERR_30  = {30, "No forward progress timeout"};
Error EXP_DL0_CERR_31  = {31, "Remote side started retraining"};
Error EXP_DL0_CERR_32  = {32, "Software retrain"};
Error EXP_DL0_CERR_33  = {33, "Lost block lock"};

Error EXP_DL0_CERR_34  = {34, "Deskew overflow"};
Error EXP_DL0_CERR_35  = {35, "Received illegal sync header"};
Error EXP_DL0_CERR_36  = {36, "EDPL threshold reached"};
Error EXP_DL0_CERR_37  = {37, "RX performance threshold breached"};
Error EXP_DL0_CERR_38  = {38, "TX performance threshold breached"};
Error EXP_DL0_CERR_39  = {39, "Training Done"};
Error EXP_DL0_CERR_40  = {40, "Remote link error bit"};
Error EXP_DL0_CERR_41  = {41, "Remote link error bit"};
Error EXP_DL0_CERR_42  = {42, "Remote link error bit"};
Error EXP_DL0_CERR_43  = {43, "Remote link error bit"};

Error EXP_DL0_CERR_44  = {44, "Remote link error bit"};
Error EXP_DL0_CERR_45  = {45, "Remote link error bit"};
Error EXP_DL0_CERR_46  = {46, "Remote link error bit"};
Error EXP_DL0_CERR_47  = {47, "A write to bit 0 will reset Error, a read will reset Error if bit 44 is set in config1 Error"};

Error* EXP_ERROR = NULL;


/*
    Initialize the i2c bus and scan for FIRE's address
*/
int explorer_i2c_init(int busnum){
    /* Getting the i2c bus number */
    char filename[20];
    int file, res;
    snprintf(filename, 19, "/dev/i2c-%d", busnum);

    /* Testing the i2c bus device */
    file = open(filename, O_RDWR);
    if (file < 0) exit(1);
    if (ioctl(file, I2C_SLAVE, EXP_I2C_ADDR) < 0) exit(1);

    /* Scanning the i2c bus for FIRE's address */
    res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE);
    if (res < 0){
        printf("ICE i2c address is not detected.\n");
        exit(1);
    }
    return file;
}

void explorer_get_firmware_info(int file){
    long long offset = 0xA000000000000000;
    long long registers[] = {0x808473880000000, 0x808473C00000000, 0x000205800000001, 0x103FF4042410007, 0x103FF4400000000, 0x103FF48FFFFFFFF,
                    0x103FF4C00000000, 0x103FF5000000000, 0x103FF5400000000, 0x103FF5800000000, 0x103FF5C00000000, 0x103FF6000000000,
                    0x103FF6400000000, 0x103FF6800000000, 0x103FF6C00000000, 0x103FF7000000000, 0x103FF7400000000, 0x103FF7800000000,
                    0x103FF7C3932F901, 0x808473080000000, 0x808473400000000};

    Register EXP_FW_REGISTERS[]  = {EXP_REG_NUM_IMAGES, EXP_REG_PARTITION_ID, EXP_REG_MAJOR_A, EXP_REG_MINOR_A, EXP_REG_BUILD_PATCH_A, EXP_REG_BUILD_NUMBER_A, EXP_REG_BUILD_DATE_A,
                     EXP_REG_MAJOR_B, EXP_REG_MINOR_B, EXP_REG_BUILD_PATCH_B, EXP_REG_BUILD_NUMBER_B, EXP_REG_BUILD_DATE_B, EXP_REG_RAM_SIZE_IN_BYTES,
                     EXP_REG_CHIP_VERSION, EXP_REG_SPI_FLASH_ID, EXP_REG_SPI_FLASH_SECTOR_SIZE, EXP_REG_SPI_FLASH_SIZE, EXP_REG_ERROR_BUFFER_SIZE, EXP_REG_IMAGE_INDEX};

    for(int i=0; i<21; i++){
        explorer_simple_write(registers[i]+offset, 5, 8, file);
        explorer_simple_read(0x2, file);
    }
    explorer_simple_write(0xA0002058, 3, 4, file);
    explorer_simple_read(0x2, file);
    explorer_simple_write(0xA0002058, 4, 4, file);
    explorer_simple_read(0x2, file);

    long long res;
    for(int i=0; i<19; i++){
        explorer_simple_write(EXP_FW_REGISTERS[i].addr, 3, 4, file);
        res = explorer_simple_read(0x2, file);
        explorer_simple_write(EXP_FW_REGISTERS[i].addr, 4, 4, file);
        res = explorer_simple_read(0x2, file);
        printf("%s : %#llx\n", EXP_FW_REGISTERS[i].label, res);
    }

    explorer_double_write(0x080108E7, 0x8000000000000000, file);
    explorer_double_write(0x00002058, 0x0000000000000001, file);

}


/*
    Read a Fire's register value.
    The operation will write a 8 bytes value representing the register address to read its value,
    followed by 8 reads of 1 byte each that form the register content.
    Both the I2C operations are done without providing any register address.
    The hardware automatically puts the result in a FIFO tied directly to I2C bus.
*/
long long explorer_simple_read(uint8_t reg, int file){
    uint8_t command = reg;    // command array, needs to be declared static
    uint8_t* buf;             // return value

    /* Sending the i2c commad */
    buf = (uint8_t*) malloc(5*sizeof(uint8_t));
    i2c_smbus_read_i2c_block_data(file, command, 5, buf);
    buf[0] = 0; // remove 0x4 that indicates read op
    return bytelist2int(buf, 5);
}

/*
    Write data in a Fire's register.
    The operation will write a 16 bytes value representing the register address
    to modify its value (8 bytes) + the data to write (8 bytes).
    It also checks if the write operation has succeeded or not.
*/
void explorer_simple_write(long long reg, uint8_t reg_type, uint8_t size, int file){
    uint8_t command[size+2];     // command array, needs to be declared static (concat of both reg address and data arrays)
    uint8_t* reg_list;       // register address as array
    /* Preparing the command content */
    reg_list = int2bytelist(reg, size);
    command[0] = reg_type;
    command[1] = size;
    for(int i=0; i<size; i++){
        command[i+2] = reg_list[i];
    }

    /* Sending the i2c commad */
    struct i2c_msg message = { EXP_I2C_ADDR, 0, sizeof(command), command };
    struct i2c_rdwr_ioctl_data ioctl_data = { &message, 1 };
    int result = ioctl(file, I2C_RDWR, &ioctl_data);
}

long long explorer_double_read(long long reg_addr, int file){
    long long bit_64, raw_reg_addr, new_reg_addr, new_reg_addr_2, res_lsb, res_msb;
    long long offset = 0xA0000000;
    bit_64 = reg_addr & (1 << 27);

    if (bit_64){
        raw_reg_addr = reg_addr & ~(1 << 27);
        new_reg_addr = (raw_reg_addr << 3) | (1 << 27);
    }
    else{
        raw_reg_addr = reg_addr;
        new_reg_addr = reg_addr;
    }

    explorer_simple_write(offset + new_reg_addr, 3, 4, file);
    explorer_simple_read(0x2, file);
    explorer_simple_write(offset + new_reg_addr, 4, 4, file);
    res_msb = explorer_simple_read(0x2, file);

    explorer_simple_read(0x2, file);

    if(bit_64){
        new_reg_addr_2 = new_reg_addr + 4;
        explorer_simple_write(offset + new_reg_addr_2, 3, 4, file);
        explorer_simple_read(0x2, file);
        explorer_simple_write(offset + new_reg_addr_2, 4, 4, file);
        res_lsb = explorer_simple_read(0x2, file);

        explorer_simple_read(0x2, file);

        return ((res_msb << 32) + res_lsb);
    }
    else return res_msb;
}

int explorer_double_write(long long reg_addr, long long data, int file){
    long long bit_64, raw_reg_addr, new_reg_addr, new_reg_addr_2, res_lsb, res_msb, data_msb, data_lsb, r_data;
    bit_64 = reg_addr & (1 << 27);
    long long offset = 0xA000000000000000;
    if (bit_64){
        raw_reg_addr = reg_addr & ~(1 << 27);
        new_reg_addr = (raw_reg_addr << 3) | (1 << 27);
        data_msb = data >> 32;
        data_lsb = data & 0xffffffff;
    }
    else{
        raw_reg_addr = reg_addr;
        new_reg_addr = reg_addr;
        data_msb = data & 0xffffffff;
        data_lsb = data & 0xffffffff;
    }

    explorer_simple_write(offset + (new_reg_addr << 32) + data_msb, 5, 8, file);
    explorer_simple_read(0x2, file);

    if (bit_64){
        explorer_simple_write(offset + ((new_reg_addr + 4) << 32) + data_lsb, 5, 8, file);
        explorer_simple_read(0x2, file);
    }
    explorer_double_read(reg_addr, file); // flush out the buffer
    r_data = explorer_double_read(reg_addr, file);

    return (r_data == data);
}

void explorer_init(int file, int freq){
    uint8_t b;
    if (freq == 333) b = 0x1;
    else if (freq == 400) b = 0x3;

    explorer_simple_write(0x00008090 + b, 1, 4, file);
    while ((explorer_simple_read(0x2, file) & ~0xffff00ff ) >> 8 != 0);
    explorer_simple_read(0x2, file);
}


void explorer_sync(int file, int freq){
    uint8_t b;
    if (freq == 333) b = 0x1;
    else if (freq == 400) b = 0x3;


    explorer_double_read(0x08040010, file);
    explorer_double_read(0x08040011, file);

    explorer_double_read(0x08012406, file);
    explorer_double_read(0x08012407, file);
    explorer_double_read(0x08012806, file);
    explorer_double_read(0x08012807, file);
    explorer_double_read(0x08040017, file);

    explorer_double_write(0x08040017, 0xf800000000000000, file);
    explorer_double_write(0x08040010, 0x0, file);
    explorer_double_write(0x08040011, 0xffffffffffffffff, file);
    explorer_double_write(0x0804000e, 0xFFFFF59E7E01FFFF, file);
    explorer_double_write(0x08012406, 0x0, file);
    explorer_double_write(0x08012407, 0x8000000000000000, file);
    explorer_double_write(0x08012404, 0x00ffffffffffffff, file);
    explorer_double_write(0x08012803, 0xffffffffffffffff, file);
    explorer_double_write(0x08012806, 0x0, file);
    explorer_double_write(0x08012807, 0x0560000000000000, file);
    explorer_double_write(0x08012804, 0x3A9FFFFFFFFFFFFF, file);

    explorer_double_read(0x08012812, file);
    explorer_double_write(0x08012812, 0x0000FFD100040000, file);

    explorer_double_read(0x08040002, file);
    explorer_double_write(0x08040002, 0x6627FFE000000000, file);

    explorer_double_read(0x08040007, file);
    explorer_double_write(0x08040007, 0x0, file);

    explorer_double_write(0x080108e4, 0x0, file);
    explorer_double_read(0x080108e4, file);

    explorer_double_read(0x08012811, file);
    explorer_double_write(0x08012811, 0x000005000000006f, file);

    explorer_double_read(0x08012810, file);
    explorer_double_write(0x08012810, 0x8122640700112620, file);

    explorer_double_read(0x08012811, file);
    explorer_simple_write(0x00008190 + b, 1, 4, file);
}

void explorer_check_sync(int file){
    long long sync_res = explorer_double_read(0x08012813, file);
    printf("%#llx\n", sync_res);
    if (sync_res & EXP_TRAINING_DONE) printf("Training successfully done.\n");
    else printf("Training failed.\n");
}
