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

from constants import *
from functions import *
from components import Eeprom
from time import sleep

##################################################################################
#    This class represents the Explorer firmware which is responsible            #
#    for initializing and functioning of unified OpenCAPI-DDR4 memory buffer.    #
#    The methods of this class give the possibility to interogate the firmware   #
#    by read/write operation through i2c bus.                                    #
##################################################################################

class Explorer:

    """ 
        Initialize i2c bus and get IDs of the Explorer 
        """
    def __init__(self, fire_freq, i2c_bus_num):
        self.i2c_bus_num = i2c_bus_num
        self.i2c_bus = init_bus(i2c_bus_num)
        self.fire_freq = fire_freq
        
        
    def getinfo(self):
        self.ecid, self.ese_mode_status = self.get_ecid()
        self.card_id = hex(self.i2c_double_read(EXP_ID_NUM_REG))

    """ 
        Detect if Explorer i2c address is visible on the bus 
        """
    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return EXP_I2C_ADDR in alive_addresses
    
    """ 
        Equivalent to GETI2C in CRONUS:
        geti2c sio 6 3 40 5 2 1 -busspeed100 -debug5.15.c          # Read 5 bytes from register @2 on the i2c address 0x40 (0x20==0x40>>1 on CRONUS)
        GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1
        GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0003

        explorer.i2c_simple_read(0x2)

        !! Warning !!
        if you have something like this in Cronus logs:
        
        GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x404A8094098|OS:0x6                
        GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                                     0400000080
        
        This is translated actually into an i2c write followed by an i2c read with the following commands:
        self.i2c_simple_write(0x404A8094098)
        self.i2c_simple_read(0x2)
        """
    def i2c_simple_read(self, reg_addr):
        res = self.i2c_bus.read_i2c_block_data(EXP_I2C_ADDR, reg_addr, 5)
        
        # format result and remove the MSB (0x04 indicates a read operation)
        odata = int(''.join(format(val, '02x') for val in res[1:5]), 16)
        logging.info("Reading {:#010x} from {:#010x}".format(odata, reg_addr))
        
        return odata

    """ 
        Equivalent to PUTI2C in CRONUS:
        puti2c sio6 3 40 0304A80940B8 -busspeed100 -debug5.15.c    # Write in register @3 the 4 bytes A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0   0304A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE
        
        explorer.i2c_simple_write(0304A80940B8)
        """
    def i2c_simple_write(self, data):
        logging.info("Writing {:#010x}".format(data))

        # calculate the number of bytes in provided data 
        length = int(len(str(hex(data)))/2)
        
        # convert to a list of bytes and then write
        msg = smbus.i2c_msg.write(EXP_I2C_ADDR, list(data.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)

    """ 
        Equivalent to i2c_double_read in CRONUS:
        Example 1:           i2c_double_read exp 08012813 -debug5.15.c
            
            i2c_double_read   : explorer:k0:n0:s0:p00 : 08012813             
            PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0    0304A8094098
            PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE                                  
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0003       
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x404A8094098|OS:0x6                
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                                     0400000080
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0004
        
            PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0    0304A809409C
            PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE                                     
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0003
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x404A809409C|OS:0x6                
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                                     0400000000
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0004
            
            i2c_double_read   : explorer:k0:n0:s0:p00 : 08012813             0000008000000000
            i2c_double_read   : explorer:k0:n0:s0:p00 : COMPLETE             0000008000000000
    
        The address bit is set in this address, which means its a 64b address and needs 2 read accesses.
        The address provided 0x08012813 will be changed following the next sequence:
            * Clear the address bit (0x08012813 -> 0x12813)
            * Shift it to left by 3 bits (0x012813<<3 = 0x94098)
            * Re-set the address bit and add the 0xA0000000 offset (0xA8094098) 
        The first part will get the MSB part of the data and the second will get the LSB from the next address.

        explorer.i2c_double_read(0x08012813)

        Example 2:          i2c_double_read exp 0020B080  -debug5.15.c
            i2c_double_read   : explorer:k0:n0:s0:p00 : 0020B080             
            PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0    0304A020B080
            PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04000F0003
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x404A020B080|OS:0x6                
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                                     0400000796
            GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
            GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04000F0004
            i2c_double_read   : explorer:k0:n0:s0:p00 : 0020B080             0000000000000796
            i2c_double_read   : explorer:k0:n0:s0:p00 : COMPLETE             0000000000000796
        
        The address bit is clear in this address, which means its a 32b address and needs only one access.
        No special operations are done on the address except adding the 0xA0000000 offset.

        explorer.i2c_double_read(0x20B080)
        """
    def i2c_double_read(self, reg_addr):
        bit_64 = reg_addr & (1 << 27)

        if bit_64:
            raw_reg_addr = reg_addr & ~(1 << 27)
            new_reg_addr = (raw_reg_addr << 3) | (1 << 27) 
        else:
            raw_reg_addr = reg_addr
            new_reg_addr = reg_addr

        self.i2c_simple_write(0x0304A0000000 + new_reg_addr)
        self.i2c_simple_read(0x2)
        self.i2c_simple_write(0x0404A0000000 + new_reg_addr)
        res_msb = self.i2c_simple_read(0x2)

        self.i2c_simple_read(0x2)
        
        if bit_64:
            new_reg_addr_2 = new_reg_addr + 4
            self.i2c_simple_write(0x0304A0000000 + new_reg_addr_2)
            self.i2c_simple_read(0x2)
            self.i2c_simple_write(0x0404A0000000 + new_reg_addr_2)
            res_lsb = self.i2c_simple_read(0x2)

            self.i2c_simple_read(0x2)

            return ((res_msb << 32) + res_lsb)

        else: return res_msb

    """
        Equivalent to i2c_double_write in CRONUS
        i2c_double_write   : explorer:k0:n0:s0:p00 : 08012811             0000040000000059
        PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0    0508A809408800000400
        PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 
        GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
        GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0005
        
        PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0    0508A809408C00000059
        PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 
        GETI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x002|OS:0x1    
        GETI2C    : sio:k0:n0:s0:p00      : COMPLETE                                 04001B0005
        
        i2c_double_write   : explorer:k0:n0:s0:p00 : 08012811             0000040000000059
        i2c_double_write   : explorer:k0:n0:s0:p00 : COMPLETE


        The first part will write the MSB of data (0x00000400) and the second one will write the LSB (0x00000059) in the next address.

        The address provided 0x08012811 will be changed following the next sequence:
            * Remove the 0x08000000 offset (0x08012811 - 0x08000000 -> 0x12811)
            * Shift it to left by 3 bits (0x012811<<3 = 0xA94088)
            * Add the following offset 0xA8000000 to the last result -> 0x94088 + 0xA8000000 = 0xA8094088
        
    

        explorer.i2c_double_write(0x08012811, 0x0000040000000059)
        """
    def i2c_double_write(self, reg_addr, data):
        bit_64 = reg_addr & (1 << 27)

        if bit_64:
            raw_reg_addr = reg_addr & ~(1 << 27)
            new_reg_addr = (raw_reg_addr << 3) | (1 << 27)
            data_msb = data >> 32
            data_lsb = data & 0xffffffff
        else:
            raw_reg_addr = reg_addr
            new_reg_addr = reg_addr
            data_msb = data & 0xffffffff
            data_lsb = data & 0xffffffff

        self.i2c_simple_write(0x0508A000000000000000 + (new_reg_addr << 32) + data_msb)
        self.i2c_simple_read(0x2)
        
        if bit_64:
            self.i2c_simple_write(0x0508A000000000000000 + ((new_reg_addr + 4) << 32) + data_lsb)
            self.i2c_simple_read(0x2)
        
        r_data = self.i2c_double_read(reg_addr)
        return (r_data == data)

    """ 
        Retreive explorer firmware info 
        """
    def get_firmware_info(self):
        logging.info("Retreiving firmware info, please wait... ")
    

        for addr in [0x0508A808473880000000, 0x0508A808473C00000000, 0x0508A000205800000001, 0x0508A103FF4042410007, 0x0508A103FF4400000000, 0x0508A103FF48FFFFFFFF,
                    0x0508A103FF4C00000000, 0x0508A103FF5000000000, 0x0508A103FF5400000000, 0x0508A103FF5800000000, 0x0508A103FF5C00000000, 0x0508A103FF6000000000,
                    0x0508A103FF6400000000, 0x0508A103FF6800000000, 0x0508A103FF6C00000000, 0x0508A103FF7000000000, 0x0508A103FF7400000000, 0x0508A103FF7800000000,
                    0x0508A103FF7C3932F901, 0x0508A808473080000000, 0x0508A808473400000000]:
            self.i2c_simple_write(addr)
            self.i2c_simple_read(0x2)

        self.i2c_simple_write(0x0304A0002058)
        self.i2c_simple_read(0x2)

        self.i2c_simple_write(0x0404A0002058)
        self.i2c_simple_read(0x2)

        for reg in EXP_FW_REGISTERS:
            self.i2c_simple_write(reg['addr'] + 0x030400000000)
            res = self.i2c_simple_read(0x2) 
            self.i2c_simple_write(reg['addr'] + 0x040400000000)
            res = self.i2c_simple_read(0x2)
            print("{}: {}".format(reg['label'], hex(res)))
            res = self.i2c_simple_read(0x2)
        
        self.i2c_double_write(0x080108E7, 0x8000000000000000)
        self.i2c_double_write(0x00002058, 0x0000000000000001)

    def init(self):
        if self.fire_freq == 333: b = 0x1
        elif self.fire_freq == 400: b = 0x3
        else: 
            print("Frequency unsupported. Expecting 333MHz or 400MHz.")
            return

       # Execute exp_omi_setup_wrap
        self.i2c_simple_write(0x010400008090 + b)
        logging.info("PUTI2C {}".format(hex(0x010400008090 + b)))
        logging.info("Waiting status flag to change from busy...")
        while (self.i2c_simple_read(0x2) & ~0xffff00ff ) >> 8 != 0: pass
        self.i2c_simple_read(0x2)

        return b

    """ 
        Start the sync/training on the explorer side. it expects Fire's frequency
        as an argument (retreived from Fire's ID).
        This should be followed by a Fire's sync/training procedure for the 
        complete training.
        """
    def sync(self):
        if self.fire_freq == 333: b = 0x1
        elif self.fire_freq == 400: b = 0x3
        else: 
            print("Frequency unsupported. Expecting 333MHz or 400MHz.")
            return

        self.i2c_double_read(0x08040010)
        self.i2c_double_read(0x08040011)

        self.i2c_double_read(0x08012406)
        self.i2c_double_read(0x08012407)
        self.i2c_double_read(0x08012806)
        self.i2c_double_read(0x08012807)
        self.i2c_double_read(0x08040017)

        self.i2c_double_write(0x08040017, 0xf800000000000000)
        self.i2c_double_write(0x08040010, 0x0)
        self.i2c_double_write(0x08040011, 0xffffffffffffffff)
        self.i2c_double_write(0x0804000e, 0xFFFFF59E7E01FFFF)
        self.i2c_double_write(0x08012406, 0x0)
        self.i2c_double_write(0x08012407, 0x8000000000000000)
        self.i2c_double_write(0x08012404, 0x00ffffffffffffff)
        self.i2c_double_write(0x08012803, 0xffffffffffffffff)
        self.i2c_double_write(0x08012806, 0x0)
        self.i2c_double_write(0x08012807, 0x0560000000000000)
        self.i2c_double_write(0x08012804, 0x3A9FFFFFFFFFFFFF)

        self.i2c_double_read(0x08012812)
        self.i2c_double_write(0x08012812, 0x0000FFD100040000)

        self.i2c_double_read(0x08040002)
        self.i2c_double_write(0x08040002, 0x6627FFE000000000)

        self.i2c_double_read(0x08040007)
        self.i2c_double_write(0x08040007, 0x0)

        self.i2c_double_write(0x080108e4, 0x0)
        self.i2c_double_read(0x080108e4)

        self.i2c_double_read(0x08012811)
        self.i2c_double_write(0x08012811, 0x000005000000006f)

        self.i2c_double_read(0x08012810)
        self.i2c_double_write(0x08012810, 0x8122640700112620)
        
        self.i2c_double_read(0x08012811)
        self.i2c_simple_write(0x010400008190 + b)
        logging.info("PUTI2C {}".format(hex(0x010400008190 + b)))

    """
        This function checks if the training is done from the Explorer side.
        It should be executed AFTER executing sync/training program on the 
        Fire's side, thus after a complete training.
        If the training has failed, It prints any errors found.
        """
    def check_sync(self):
        sync_res = self.i2c_double_read(0x08012813)
        print(hex(sync_res))
        if (sync_res & EXP_TRAINING_DONE) : 
            print("Training successfully done.")
            return 1

        if sync_res == 0: print("Training failed.")
        self.get_errors(sync_res)

        return 0

    """
        Get the sync result after a failed training and returns found errors.
        """
    def get_errors(self, sync_res):
        for err in EXP_ERRORS:
            if err['bit'] == 39: continue
            if sync_res & (1 << err['bit']): print("Error in bit {}: {}".format(err['bit'], err['label']))
        print('\n')

    """
        Retreive Explorer's ECID and Entreprise Mode Status.
        """
    def get_ecid(self):
        ese_mode_status = self.i2c_double_read(0x0020B080)
        addr_i = 0x0020B0C4
        ecid = []
        while addr_i >= 0x0020B090:
            ecid.append(self.i2c_double_read(addr_i))
            addr_i -= 4
        ecid_n = int(''.join(format(val, '02x') for val in ecid), 16)
        return hex(ecid_n), hex(ese_mode_status)

    def i2cread(self, reg_addr):
        res = self.i2c_bus.read_i2c_block_data(EXP_I2C_ADDR, reg_addr, 5)
        
        # format result and remove the MSB (0x04 indicates a read operation)
        odata = int(''.join(format(val, '02x') for val in res[1:5]), 16)
        logging.info("Reading {:#010x} from {:#010x}".format(odata, reg_addr))
        
        return odata
    
    """ 
        Equivalent to PUTI2C in CRONUS:
        puti2c sio6 3 40 0304A80940B8 -busspeed100 -debug5.15.c    # Write in register @3 the 4 bytes A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0   0304A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE
        
        explorer.i2cwrite(0304A80940B8)
        """
    def i2cwrite(self, data):
        logging.info("Writing {:#010x}".format(data))

        # calculate the number of bytes in provided data 
        length = int(len(str(hex(data)))/2)
        
        # convert to a list of bytes and then write
        msg = smbus.i2c_msg.write(EXP_I2C_ADDR, list(data.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    explorer = Explorer(333, 3)
    # explorer.i2c_simple_write(0x0304A020B080)
    # print(hex(explorer.i2c_simple_read(0x2)))
    # explorer.i2c_simple_write(0x0404A020B080)
    # print(hex(explorer.i2c_simple_read(0x2)))
    # print(hex(explorer.i2c_simple_read(0x2)))

    explorer.i2c_double_write(0x08012811, 0x0000040000000058)
    print(hex(explorer.i2c_double_read(0x08012811)))