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

class Ice:

    """ 
        Initialize i2c bus and get IDs of the Gemini 
        """
    def __init__(self, fire_freq, i2c_bus_num=3):
        self.i2c_bus_num = i2c_bus_num
        self.i2c_bus = init_bus(i2c_bus_num)
        

    """ 
        Detect if Explorer i2c address is visible on the bus 
        """
    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return ICE_I2C_ADDR in alive_addresses
    
    def i2c_simple_read(self, reg_addr):
        length = int(len(str(hex(reg_addr)))/2)
        msg = smbus.i2c_msg.write(ICE_I2C_ADDR, list(reg_addr.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)
        # if size read is more than available, the program will crash
        block = []
        for i in range(5):
            d = self.i2c_bus.read_byte(ICE_I2C_ADDR)
            block.append(d)

        # take only the first 8 bytes
        odata = int(''.join(format(val, '02x') for val in block[1:5]), 16)

        logging.info("Reading {:#010x} from {:#010x}".format(odata, reg_addr))
            
        return odata

    def i2c_simple_write(self, data):
        length = int(len(str(hex(data)))/2)
        msg = smbus.i2c_msg.write(ICE_I2C_ADDR, list(data.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)
    

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
        res_msb = self.i2c_simple_read(0x404A0000000 + new_reg_addr)

        self.i2c_simple_read(0x2)
        
        if bit_64:
            new_reg_addr_2 = new_reg_addr + 4
            self.i2c_simple_write(0x0304A0000000 + new_reg_addr_2)
            self.i2c_simple_read(0x2)
            res_lsb = self.i2c_simple_read(0x404A0000000 + new_reg_addr_2)

            self.i2c_simple_read(0x2)

            return ((res_msb << 32) + res_lsb)

        else: return res_msb

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

        print("data lsb: ", hex(data_lsb))
        print("data msb: ", hex(data_msb))
        
        print("write 1: ", hex(0x0508A000000000000000 + (new_reg_addr << 32) + data_msb))
        self.i2c_simple_write(0x0508A000000000000000 + (new_reg_addr << 32) + data_msb)
        self.i2c_simple_read(0x2)
        
        if bit_64:
            self.i2c_simple_write(0x0508A000000000000000 + ((new_reg_addr + 4) << 32) + data_lsb)
            print("write 1: ", hex(0x0508A000000000000000 + ((new_reg_addr + 4) << 32) + data_lsb))
            self.i2c_simple_read(0x2)

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    ice = Ice(333)
    # explorer.i2cwrite(0x0508A808473400000000)
    # print(hex(ice.i2c_simple_read(0x404A8092070)))
    # print(hex(ice.i2c_double_read(0x26c)))
    # TODO : CHECK 64 bytes !!!!!!!!!!!!!!!!! before choosing which function to use
    ice.i2c_double_write(0x801240c, 0x81)
    print(hex(ice.i2c_double_read(0x801240c)))