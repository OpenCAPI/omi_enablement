#include "components.h"

int mux_i2c_init(int muxaddr, int busnum){
    /* Getting the i2c bus number */
    char filename[20];
    int file, res;
    snprintf(filename, 19, "/dev/i2c-%d", busnum);

    /* Testing the i2c bus device */
    file = open(filename, O_RDWR);
    if (file < 0) exit(1);
    if (ioctl(file, I2C_SLAVE, muxaddr) < 0) exit(1);

    /* Scanning the i2c bus for FIRE's address */
    res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE);
    if (res < 0){
        printf("Mux %#x i2c address is not detected.\n", muxaddr);
        exit(1);
    }
    return file;
}

uint8_t mux_read(int file){
    uint8_t buf;
    read(file, &buf, 1);
    return buf;
}

void mux_write(uint8_t muxaddr, uint8_t data, int file){
    uint8_t command[1];
    command[0] = data;
    /* Sending the i2c commad */
    struct i2c_msg message = { muxaddr, 0, sizeof(command), command };
    struct i2c_rdwr_ioctl_data ioctl_data = { &message, 1 };
    int result = ioctl(file, I2C_RDWR, &ioctl_data);
}



int pmic_i2c_init(int pmicaddr, int busnum){
    /* Getting the i2c bus number */
    char filename[20];
    int file, res;
    snprintf(filename, 19, "/dev/i2c-%d", busnum);

    /* Testing the i2c bus device */
    file = open(filename, O_RDWR);
    if (file < 0) exit(1);
    if (ioctl(file, I2C_SLAVE, pmicaddr) < 0) exit(1);

    /* Scanning the i2c bus for FIRE's address */
    res = i2c_smbus_write_quick(file, I2C_SMBUS_WRITE);
    if (res < 0){
        printf("PMIC %#x i2c address is not detected.\n", pmicaddr   );
        exit(1);
    }
    return file;
}
uint8_t pmic_read(int file){
    uint8_t buf;             // return value

    /* Sending the i2c commad */
    i2c_smbus_read_i2c_block_data(file, 0x32, 1, &buf);
    return buf;
}
void pmic_write(uint8_t pmicaddr, uint8_t data, int file){
    char d[] = {data};
    i2c_smbus_write_i2c_block_data(file, 0x32, 1, d);
}


void open_path(int busnum){
    int file = mux_i2c_init(MUX2_I2C_ADDR, busnum);
    mux_write(MUX2_I2C_ADDR, 1, file);
}
void close_path(int busnum){
    int file = mux_i2c_init(MUX2_I2C_ADDR, busnum);
    mux_write(MUX2_I2C_ADDR, 0, file);
}
void set_pmics(int busnum){
    int file;
    file = pmic_i2c_init(PMIC1_I2C_ADDR, busnum);
    pmic_write(PMIC1_I2C_ADDR, 0x80, file);
    file = pmic_i2c_init(PMIC2_I2C_ADDR, busnum);
    pmic_write(PMIC2_I2C_ADDR, 0x80, file);
}
void clear_pmics(int busnum){
    int file;
    file = pmic_i2c_init(PMIC1_I2C_ADDR, busnum);
    pmic_write(PMIC1_I2C_ADDR, 0, file);
    file = pmic_i2c_init(PMIC2_I2C_ADDR, busnum);
    pmic_write(PMIC2_I2C_ADDR, 0, file);
}
void setup_ddimm_path(int busnum, char* ddimms){
	printf("Openning path:\n");
    open_path(busnum);
    int file = mux_i2c_init(MUX3_I2C_ADDR, busnum);
    if (strcmp(ddimms, "none") == 0) mux_write(MUX3_I2C_ADDR, 0, file);
    if (strcmp(ddimms, "a") == 0) {
        mux_write(MUX3_I2C_ADDR, (1 << DDIMMA), file);
        sleep(2);
        set_pmics(busnum);
    }
    else if (strcmp(ddimms, "b") == 0) {
        mux_write(MUX3_I2C_ADDR, (1 << DDIMMB), file);
        sleep(2);
        set_pmics(busnum);
    }
}
