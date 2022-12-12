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
    def __init__(self, fire_freq, i2c_bus_num):
        self.i2c_bus_num = i2c_bus_num
        self.i2c_bus = init_bus(i2c_bus_num)
        self.fire_freq = fire_freq
        self.fire_freq = 333
    
    def getinfo(self):
        print("ICE FPGA info:")
        Id_reg = self.i2c_double_read(ICE_ID_NUM_REG)
        print(" ID            =",hex(Id_reg))
        Ice_git_rev  = (Id_reg >> 32) & 0x0FFFFFFF
        Ice_dirty    = ((Id_reg >> 32) & FIRE_ID_DIRTY_BIT) >> 28
        Ice_freq_raw = ((Id_reg >> 32) & FIRE_ID_FREQ_DEF) >> 29
        if Ice_freq_raw == 3: Ice_freq = "400 MHz"
        else:                 Ice_freq = "333 MHz"

        Maj_rel      = (Id_reg & 0xF0000000)>>28
        Min_rel      = (Id_reg & 0x0F000000)>>24
        #Reserved    = (Id_reg & 0x00F00000)>>20
        #Loc_code    = (Id_reg & 0x000F0000)>>16
        Chip_ID      = (Id_reg & 0x000000FF)
        print(" ICE git rev   =",hex(Ice_git_rev))
        print(" ICE dirty bit =",hex(Ice_dirty))
        print(" ICE Frequency =",Ice_freq)
        print(" Release       =",Maj_rel,end=".")
        print(Min_rel)
        #print(" Reserved      =",hex(Reserved))
        #print(" Location Code =",hex(Loc_code))
        print(" Chip ID       =",hex(Chip_ID))

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
        # if size of read is more than available, the program will crash
        block = []
        for i in range(5):
            d = self.i2c_bus.read_byte(ICE_I2C_ADDR)
            block.append(d)

        # take only the first 8 bytes
        odata = int(''.join(format(val, '02x') for val in block[1:5]), 16)
        logging.info("ICE: Reading {} from {}".format(hex(odata), hex(reg_addr)))
        #logging.info("ICE: Reading {:#010x} from {:#010x}".format(odata, reg_addr))
        if odata   == 0xdec0de00:
        	print("WARNING !! ICE address has not been set yet by hardware")
        elif odata == 0xdec0de0b:
        	print("ERROR !! ICe address is in AXI range but out of the hardware range")
        
            
        return odata

    def i2c_simple_write(self, data):
        logging.info("ICE: Writing {:#010x}".format(data))
        
        # calculate the number of bytes in provided data
        length = int(len(str(hex(data)))/2)

        # convert to a list of bytes and then write
        msg = smbus.i2c_msg.write(ICE_I2C_ADDR, list(data.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)
    

    def i2c_double_read(self, reg_addr):
        bit_64 = reg_addr & (1 << 27)    # if bit64 this means we need to achieve 2 I2C transactions

        if bit_64:
            raw_reg_addr = reg_addr & ~(1 << 27)
            new_reg_addr = (raw_reg_addr << 3) | (1 << 27)
            logging.info("DBG: ICE: 64bits DRead at Scom Addr: {:#010x}".format(reg_addr))  
        else:
            raw_reg_addr = reg_addr
            new_reg_addr = reg_addr
            logging.info("       ICE: 32bits  Read at Scom Addr: {:#010x}".format(reg_addr))
        logging.info("       ICE: read at Register Addr:     {:#010x}".format(new_reg_addr))

        try:
            self.i2c_simple_read(0x2)  # This prevents reading unexisting address, as we can't 100% mimic CRONUS proper behavior yet
        except:
            print("WARNING ! ICE read failed")
            exit()
        self.i2c_simple_write(0x0304A0000000 + new_reg_addr)
        self.i2c_simple_read(0x2)
        # ICE affects directly the result as a response to the read
        res_msb = self.i2c_simple_read(0x0404A0000000 + new_reg_addr) # MSBs of 64 or 32 bits reg content value

        self.i2c_simple_read(0x2)   # previous command status
        
        if bit_64:
            new_reg_addr_2 = new_reg_addr + 4
            logging.info("       ICE: read at Register Addr:     {:#010x}".format(new_reg_addr_2))
            
            # first previous test should be enough, but ...
            try:
                self.i2c_simple_read(0x2)  # This prevents reading unexisting address, as we can't 100% mimic CRONUS proper behavior yet
            except:
                print("ERROR ! ICE: read failed")
                exit()

            self.i2c_simple_write(0x0304A0000000 + new_reg_addr_2)
            self.i2c_simple_read(0x2)
            # ICE affects directly the result as a response to the read
            res_lsb = self.i2c_simple_read(0x0404A0000000 + new_reg_addr_2)
                    
            self.i2c_simple_read(0x2) # previous command status

            return ((res_msb << 32) + res_lsb)

        else: return res_msb

    def i2c_double_write(self, reg_addr, data):
        bit_64 = reg_addr & (1 << 27)
        logging.info("ICE DWrite Reg: {:#010x} with Data:{:#010x}".format(reg_addr, data))
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

        #print("data lsb: ", hex(data_lsb))
        #print("data msb: ", hex(data_msb))
        #print("write : ", hex(0x0508A000000000000000 + (new_reg_addr << 32) + data_msb))
        self.i2c_simple_write(0x0508A000000000000000 + (new_reg_addr << 32) + data_msb)
        self.i2c_simple_read(0x2)
        
        if bit_64:
            self.i2c_simple_write(0x0508A000000000000000 + ((new_reg_addr + 4) << 32) + data_lsb)
            #print("write : ", hex(0x0508A000000000000000 + ((new_reg_addr + 4) << 32) + data_lsb))
            self.i2c_simple_read(0x2)

    def i2cread(self, reg_addr):
        #length = int(len(str(hex(reg_addr)))/2)
        # ICE hardware allows reading only if 0x02 is received as message.
        if reg_addr != 0x2:
            print("ERROR !! i2cread is only valid for register 0x02!")
            exit()
        # WARNING the read_i2c_block_data routine will use only the LSByte of reg_addr
        # https://buildmedia.readthedocs.org/media/pdf/smbus2/latest/smbus2.pdf
        res = self.i2c_bus.read_i2c_block_data(ICE_I2C_ADDR, reg_addr, 5)
        # format result and remove the MSB (0x04 indicates a read operation)
        odata = int(''.join(format(val, '02x') for val in res[1:5]), 16)
        logging.info("ICE: Reading {} from {}".format(hex(odata), hex(reg_addr)))
        if odata   == 0xdec0de00:
        	print("WARNING !! ICE address has not been set yet by hardware")
        elif odata == 0xdec0de0b:
        	print("ERROR !! ICE address is out of the hardware range")
        
        #logging.info("ICE: Reading {:#010x} from {:#010x}".format(odata, reg_addr))
        
        return odata
    
    """ 
        Equivalent to PUTI2C in CRONUS:
        puti2c sio6 3 40 0304A80940B8 -busspeed100 -debug5.15.c    # Write in register @3 the 4 bytes A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : E: 6|P:30|A:0x20|S:100|O:0x000|OS:0x0   0304A80940B8
        PUTI2C    : sio:k0:n0:s0:p00      : COMPLETE
        
        explorer.i2cwrite(0304A80940B8)
        """
    def i2cwrite(self, data):
        logging.info("ICE Writing data:{:#010x}".format(data))

        # calculate the number of bytes in provided data 
        length = int(len(str(hex(data)))/2)
        
        # convert to a list of bytes and then write
        msg = smbus.i2c_msg.write(ICE_I2C_ADDR, list(data.to_bytes(length, 'big')))
        self.i2c_bus.i2c_rdwr(msg)



    def init(self):
        print("ice.init() : Apparently there's not much to do here as hardware handles all ?? !!")

    def sync(self):
        if self.fire_freq == 333: b = 0x1
        elif self.fire_freq == 400: b = 0x3
        else: 
            print("Frequency unsupported. Expecting 333MHz or 400MHz.")
            return

        print("---------- Step XX : ICE OMI Training Sequence ------------")
        print("---------- ice.sync() : TO BE DONE             ------------")

'''def check_sync(self):
        if self.fire_freq == 333: b = 0x1
        elif self.fire_freq == 400: b = 0x3
        else: 
            print("Frequency unsupported. Expecting 333MHz or 400MHz.")
            return
        print(hex(self.i2c_double_read(0x08012424)))'''
        


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    ice = Ice(333, 3)
    # explorer.i2cwrite(0x0508A808473400000000)
    # print(hex(ice.i2c_simple_read(0x404A8092070)))
    # print(hex(ice.i2c_double_read(0x26c)))
    # TODO : CHECK 64 bytes !!!!!!!!!!!!!!!!! before choosing which function to use
    ice.i2c_double_write(0x801240c, 0x81)
    print(hex(ice.i2c_double_read(0x801240c)))

    print(hex(ice.i2c_double_read(0x08012424)))
