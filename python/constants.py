#
# Copyright 2019 International Business Machines
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

#########################################################
#                                                       #
#                         ICE                           #
#                                                       #
#########################################################

ICE_I2C_ADDR                  = 0x20



#########################################################
#                                                       #
#                        EXPLORER                       #
#                                                       #
#########################################################

# General attributes
EXP_I2C_ADDR                  = 0x20
EXP_ADDR_OFFSET               = 0xA0000000

# Firmware registers
EXP_REG_NUM_IMAGES            = {'addr': 0x102FF00 + EXP_ADDR_OFFSET, 'label': 'FW number of images'}
EXP_REG_PARTITION_ID          = {'addr': 0x102FF04 + EXP_ADDR_OFFSET, 'label': 'Partition ID'}

EXP_REG_MAJOR_A                = {'addr': 0x102FF08 + EXP_ADDR_OFFSET, 'label': 'Major (Boot Partion A)'}
EXP_REG_MINOR_A                = {'addr': 0x102FF0C + EXP_ADDR_OFFSET, 'label': 'Minor (Boot Partion A)'}
EXP_REG_BUILD_PATCH_A          = {'addr': 0x102FF10 + EXP_ADDR_OFFSET, 'label': 'Build patch (Boot Partion A)'}
EXP_REG_BUILD_NUMBER_A         = {'addr': 0x102FF14 + EXP_ADDR_OFFSET, 'label': 'Build number (Boot Partion A)'}
EXP_REG_BUILD_DATE_A           = {'addr': 0x102FF18 + EXP_ADDR_OFFSET, 'label': 'Build date (Boot Partion A)'}

EXP_REG_MAJOR_B                = {'addr': 0x102FF1C + EXP_ADDR_OFFSET, 'label': 'Major (Boot Partion B)'}
EXP_REG_MINOR_B                = {'addr': 0x102FF20 + EXP_ADDR_OFFSET, 'label': 'Minor (Boot Partion B)'}
EXP_REG_BUILD_PATCH_B          = {'addr': 0x102FF24 + EXP_ADDR_OFFSET, 'label': 'Build patch (Boot Partion B)'}
EXP_REG_BUILD_NUMBER_B         = {'addr': 0x102FF28 + EXP_ADDR_OFFSET, 'label': 'Build number (Boot Partion B)'}
EXP_REG_BUILD_DATE_B           = {'addr': 0x102FF2C + EXP_ADDR_OFFSET, 'label': 'Build date (Boot Partion B)'}

EXP_REG_RAM_SIZE_IN_BYTES     = {'addr': 0x102FF30 + EXP_ADDR_OFFSET, 'label': 'RAM size (in bytes)'}
EXP_REG_CHIP_VERSION          = {'addr': 0x102FF34 + EXP_ADDR_OFFSET, 'label': 'Chip version'}
EXP_REG_SPI_FLASH_ID          = {'addr': 0x102FF38 + EXP_ADDR_OFFSET, 'label': 'SPI flash ID'}
EXP_REG_SPI_FLASH_SECTOR_SIZE = {'addr': 0x102FF3C + EXP_ADDR_OFFSET, 'label': 'SPI flash sector size'}
EXP_REG_SPI_FLASH_SIZE        = {'addr': 0x102FF40 + EXP_ADDR_OFFSET, 'label': 'SPI flash size'}
EXP_REG_ERROR_BUFFER_SIZE     = {'addr': 0x102FF44 + EXP_ADDR_OFFSET, 'label': 'Error buffer size'}
EXP_REG_IMAGE_INDEX           = {'addr': 0x102FF48 + EXP_ADDR_OFFSET, 'label': 'Image index'}

EXP_FW_REGISTERS = [EXP_REG_NUM_IMAGES, EXP_REG_PARTITION_ID, EXP_REG_MAJOR_A, EXP_REG_MINOR_A, EXP_REG_BUILD_PATCH_A, EXP_REG_BUILD_NUMBER_A, EXP_REG_BUILD_DATE_A, 
                    EXP_REG_MAJOR_B, EXP_REG_MINOR_B, EXP_REG_BUILD_PATCH_B, EXP_REG_BUILD_NUMBER_B, EXP_REG_BUILD_DATE_B, EXP_REG_RAM_SIZE_IN_BYTES,
                    EXP_REG_CHIP_VERSION, EXP_REG_SPI_FLASH_ID, EXP_REG_SPI_FLASH_SECTOR_SIZE, EXP_REG_SPI_FLASH_SIZE, EXP_REG_ERROR_BUFFER_SIZE, EXP_REG_IMAGE_INDEX]

# Training and errors
EXP_TRAINING_DONE  = (1 << 39)

EXP_DL0_CERR_00  = {'bit': 0, 'label': 'UE on control flit frame buffer'}
EXP_DL0_CERR_01  = {'bit': 1, 'label': 'UE on control flit replay buffer'}
EXP_DL0_CERR_02  = {'bit': 2, 'label': 'Ack pointer overflow'}
EXP_DL0_CERR_03  = {'bit': 3, 'label': 'Illegal run length from TL'}

EXP_DL0_CERR_04  = {'bit': 4, 'label': 'Truncated flit from TL'}
EXP_DL0_CERR_05  = {'bit': 5, 'label': 'Data parity error'}
EXP_DL0_CERR_06  = {'bit': 6, 'label': 'Control parity error'}
EXP_DL0_CERR_07  = {'bit': 7, 'label': 'RX receiving illegal run length'}
EXP_DL0_CERR_08  = {'bit': 8, 'label': 'RX receiving slow'}
EXP_DL0_CERR_09  = {'bit': 9, 'label': 'Illegal Tx Lane reversal request'}
EXP_DL0_CERR_10  = {'bit': 10, 'label': 'Flit Hammer. Detected a possible DI and brought the link down to prevent the potential data corruption'}
EXP_DL0_CERR_11  = {'bit': 11, 'label': 'Spare'}
EXP_DL0_CERR_12  = {'bit': 12, 'label': 'ECC UE on data flit frame buffer'}
EXP_DL0_CERR_13  = {'bit': 13, 'label': 'ECC UE on data flit replay buffer'}

EXP_DL0_CERR_14  = {'bit': 14, 'label': 'ECC CE error frame buffer'}
EXP_DL0_CERR_15  = {'bit': 15, 'label': 'ECC CE error replay buffer'}
EXP_DL0_CERR_16  = {'bit': 16, 'label': 'CRC error detected'}
EXP_DL0_CERR_17  = {'bit': 17, 'label': 'NACK received'}
EXP_DL0_CERR_18  = {'bit': 18, 'label': 'TX side in x4 mode'}
EXP_DL0_CERR_19  = {'bit': 19, 'label': 'RX side in x4 mode'}
EXP_DL0_CERR_20  = {'bit': 20, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_21  = {'bit': 21, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_22  = {'bit': 22, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_23  = {'bit': 23, 'label': 'EDPL parity error on lane'}

EXP_DL0_CERR_24  = {'bit': 24, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_25  = {'bit': 25, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_26  = {'bit': 26, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_27  = {'bit': 27, 'label': 'EDPL parity error on lane'}
EXP_DL0_CERR_28  = {'bit': 28, 'label': 'Spare'}
EXP_DL0_CERR_29  = {'bit': 29, 'label': 'Tx_Flit macro detected a reason to retrain the link. Look at CYA register for details'}
EXP_DL0_CERR_30  = {'bit': 30, 'label': 'No forward progress timeout'}
EXP_DL0_CERR_31  = {'bit': 31, 'label': 'Remote side started retraining'}
EXP_DL0_CERR_32  = {'bit': 32, 'label': 'Software retrain'}
EXP_DL0_CERR_33  = {'bit': 33, 'label': 'Lost block lock'}

EXP_DL0_CERR_34  = {'bit': 34, 'label': 'Deskew overflow'}
EXP_DL0_CERR_35  = {'bit': 35, 'label': 'Received illegal sync header'}
EXP_DL0_CERR_36  = {'bit': 36, 'label': 'EDPL threshold reached'}
EXP_DL0_CERR_37  = {'bit': 37, 'label': 'RX performance threshold breached'}
EXP_DL0_CERR_38  = {'bit': 38, 'label': 'TX performance threshold breached'}
EXP_DL0_CERR_39  = {'bit': 39, 'label': 'Training Done'}
EXP_DL0_CERR_40  = {'bit': 40, 'label': 'Remote link error bit'}
EXP_DL0_CERR_41  = {'bit': 41, 'label': 'Remote link error bit'}
EXP_DL0_CERR_42  = {'bit': 42, 'label': 'Remote link error bit'}
EXP_DL0_CERR_43  = {'bit': 43, 'label': 'Remote link error bit'}

EXP_DL0_CERR_44  = {'bit': 44, 'label': 'Remote link error bit'}
EXP_DL0_CERR_45  = {'bit': 45, 'label': 'Remote link error bit'}
EXP_DL0_CERR_46  = {'bit': 46, 'label': 'Remote link error bit'}
EXP_DL0_CERR_47  = {'bit': 47, 'label': 'A write to bit 0 will reset register, a read will reset register if bit 44 is set in config1 register'}

EXP_ERRORS = [EXP_DL0_CERR_00, EXP_DL0_CERR_01, EXP_DL0_CERR_02, EXP_DL0_CERR_03, EXP_DL0_CERR_04, EXP_DL0_CERR_05, EXP_DL0_CERR_06, EXP_DL0_CERR_07, 
            EXP_DL0_CERR_08, EXP_DL0_CERR_09, EXP_DL0_CERR_10, EXP_DL0_CERR_11, EXP_DL0_CERR_12, EXP_DL0_CERR_13, EXP_DL0_CERR_14, EXP_DL0_CERR_15, 
            EXP_DL0_CERR_16, EXP_DL0_CERR_17, EXP_DL0_CERR_18, EXP_DL0_CERR_19, EXP_DL0_CERR_20, EXP_DL0_CERR_21, EXP_DL0_CERR_22, EXP_DL0_CERR_23, 
            EXP_DL0_CERR_24, EXP_DL0_CERR_25, EXP_DL0_CERR_26, EXP_DL0_CERR_27, EXP_DL0_CERR_28, EXP_DL0_CERR_29, EXP_DL0_CERR_30, EXP_DL0_CERR_31, 
            EXP_DL0_CERR_32, EXP_DL0_CERR_33, EXP_DL0_CERR_34, EXP_DL0_CERR_35, EXP_DL0_CERR_36, EXP_DL0_CERR_37, EXP_DL0_CERR_38, EXP_DL0_CERR_39, 
            EXP_DL0_CERR_40, EXP_DL0_CERR_41, EXP_DL0_CERR_42, EXP_DL0_CERR_43, EXP_DL0_CERR_44, EXP_DL0_CERR_45, EXP_DL0_CERR_46, EXP_DL0_CERR_47]

EXP_ID_NUM_REG   = 0x02090000

#########################################################
#                                                       #
#                         FIRE                          #
#                                                       #
#########################################################

FIRE_I2C_ADDR          = 0x38

FIRE_400_MHZ_VERSION_ID = [0xb20b168, 0x90AD53D, 0xA032D32, 0x93A2CD0]
FIRE_333_MHZ_VERSION_ID = [0x5cd07be, 0xE525BAD, 0xB20B168]

FIRE_FML_REG_BASE_ADDR = 0x0100000000000000
FIRE_C3S_REG_BASE_ADDR = 0x0101000000000000
FIRE_FBIST_REG_BASE_ADDR = 0x0102000000000000

FIRE_FML_FIRE_VERSION_REG    = FIRE_FML_REG_BASE_ADDR + 0x00
FIRE_FML_RESET_CONTROL_REG    = FIRE_FML_REG_BASE_ADDR + 0x04
FIRE_FML_LED_CONTROL_REG    = FIRE_FML_REG_BASE_ADDR + 0x08
FIRE_FML_LED_OVERRIDE_REG    = FIRE_FML_REG_BASE_ADDR + 0x0c

FIRE_FML_DDMIMM_DETECT_REG   = FIRE_FML_REG_BASE_ADDR + 0x20

FIRE_FML_DDIMMA_RESET_BIT    = (1 << 3)
FIRE_FML_DDIMMB_RESET_BIT    = (1 << 2)
FIRE_FML_DDIMMC_RESET_BIT    = (1 << 1)
FIRE_FML_DDIMMD_RESET_BIT    = (1 << 0)
FIRE_FML_DDIMMW_RESET_BIT    = (1 << 4)

FIRE_ID_DIRTY_BIT = (1 << 28)
FIRE_ID_FREQ_DEF  = (7 << 29)

FIRE_FML_LED_DDIMMW_RED_OVERRIDE_EN = (1 << 17)
FIRE_FML_LED_DDIMMW_GREEN_OVERRIDE_EN = (1 << 16)
FIRE_FML_LED_DDIMMA_RED_OVERRIDE_EN = (1 << 13)
FIRE_FML_LED_DDIMMA_GREEN_OVERRIDE_EN = (1 << 12)
FIRE_FML_LED_DDIMMB_RED_OVERRIDE_EN = (1 << 9)
FIRE_FML_LED_DDIMMB_GREEN_OVERRIDE_EN = (1 << 8)
FIRE_FML_LED_DDIMMC_RED_OVERRIDE_EN = (1 << 5)
FIRE_FML_LED_DDIMMC_GREEN_OVERRIDE_EN = (1 << 4)
FIRE_FML_LED_DDIMMD_RED_OVERRIDE_EN = (1 << 1)
FIRE_FML_LED_DDIMMD_GREEN_OVERRIDE_EN = (1 << 0)

I2C_REG_NOT_FOUND_READ_ERROR = 0xDEC0DE1C

# --------------- C3S -------------- #
C3S_OFFSET                        = 0x0101000000000000
REG_C3S_RESP_CNTL                 = 0x00030004
REG_C3S_CNTL                      = 0x00030000
FIELD_C3S_RESP_WRITE_ADDR_RESET   = 9
FIELD_C3S_START                   = 0
FIELD_C3S_DONE                    = 3
FIELD_C3S_STOP                    = 1

# -------------- Config Host --------------- #

FIRE_DDIMMA_HOST_CONF_BASE_ADDR = 0x0104000000000000
FIRE_DDIMMB_HOST_CONF_BASE_ADDR = 0x0104040000000000
FIRE_DDIMMC_HOST_CONF_BASE_ADDR = 0x0104080000000000
FIRE_DDIMMD_HOST_CONF_BASE_ADDR = 0x01040C0000000000

FIRE_DDIMMA_OPENCAPI_DL_CONTROL = FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10
FIRE_DDIMMB_OPENCAPI_DL_CONTROL = FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10

FIRE_DDIMMA_HOST_CONF_STATUS_REG = FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x20
FIRE_DDIMMB_HOST_CONF_STATUS_REG = FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x20

DDIMM_HOST_CONF_UP_BIT = (1 << 3)


#########################################################
#                                                       #
#                     COMPONENTS                        #
#                                                       #
#########################################################

MUX1_I2C_ADDR = 0x70
MUX2_I2C_ADDR = 0x73
MUX3_I2C_ADDR = 0x71

PMIC1_I2C_ADDR = 0x4f
PMIC2_I2C_ADDR = 0x67

DDIMMA = 0
DDIMMB = 1

EEPROM_I2C_ADDR = 0x50
POWER_CTRL_I2C_ADDR = 0x64
I2C_ADDR_RANGE = 127

EXPLORER   = {"name": "EXPLORER/ICE", "addr": EXP_I2C_ADDR}
FIRE       = {"name": "FIRE", "addr": FIRE_I2C_ADDR}
MUX1       = {"name": "Apollo First Level Switch/Mux/Selector", "addr": MUX1_I2C_ADDR}
MUX2       = {"name": "Dummy Switch/Mux/Selector for Apollo16 Config", "addr": MUX2_I2C_ADDR}
MUX3       = {"name": "DDIMM Switch/Mux/Selector", "addr": MUX3_I2C_ADDR}
EEPROM     = {"name": "EEPROM", "addr": EEPROM_I2C_ADDR}
POWER_CTRL = {"name": "UDC90120A Power Controller", "addr": POWER_CTRL_I2C_ADDR}
PMIC1      = {"name": "PMIC1", "addr": PMIC1_I2C_ADDR}
PMIC2      = {"name": "PMIC2", "addr": PMIC2_I2C_ADDR}

known_devices = [EXPLORER, FIRE, MUX1, MUX2, MUX3, EEPROM, POWER_CTRL, PMIC1, PMIC2]