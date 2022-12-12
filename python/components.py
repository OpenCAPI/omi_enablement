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
from time import sleep
#
#
#
#
#
#
##################################################################################
#   This class represents the muxes AKA selectors AKA switches implemented       #
#   in the TORMem card.                                                          #
#                                                                                #
#           0x73                      0x71                                       #   
#            ---------                 ---------                                 #
#           |       0|--------------->|       0|-----------------> DDIMMA/0      #
#           |       1|                |       1|-----------------> DDIMMB/1      #
#           |       2|                |       2|                                 #
#           |       3|                |       3|                                 #
#           ---------                ...      ...                                #
#                                                                                #
#   Muxes are accessible through I2C. 0x73 Mux is always presents on the bus.    #
#   To open path to 0x71 mux, write 0x1 to @0x73.                                #
#   After that: to access DDIMMA, write 0x0 to 0x71, to access DDIMMB,           #
#               write 0x1 to @0x71.                                              #
##################################################################################
class Mux:
    def __init__(self, i2c_addr, i2c_bus_num):
        self.i2c_addr = i2c_addr
        self.i2c_bus = init_bus(i2c_bus_num)
    
    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return self.i2c_addr in alive_addresses

    def i2cwrite(self, data):
        msg = smbus.i2c_msg.write(self.i2c_addr, [data])
        self.i2c_bus.i2c_rdwr(msg)
        logging.info("Mux with address ({:#02x}) is set to {:#02x}".format(self.i2c_addr, data))
    
    def i2cread(self):
        res = self.i2c_bus.read_byte(self.i2c_addr)
        return res


##################################################################################
#   This class represents the pmics that give access to the Explorer chip        #
#   They are visible only when the path to a DDIMM is open.                      #
#   Writing 0x80 at @0x32 on both of them gives access to the Explorer.          #
#   Default value is 0x00 at @0x32.                                              #
##################################################################################
class Pmic:
    def __init__(self, i2c_addr, i2c_bus_num):
        self.i2c_addr = i2c_addr
        self.i2c_bus = init_bus(i2c_bus_num)
    
    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return self.i2c_addr in alive_addresses

    def i2cwrite(self, data):
        self.i2c_bus.write_i2c_block_data(self.i2c_addr, 0x32, [data])
        res = self.i2cread()
        if res == data: logging.info("PMIC {} value successfully changed to {}.".format(hex(self.i2c_addr), hex(data)))
        else : logging.info("Couldn't change PMIC {} value ({}) to {}.".format(hex(self.i2c_addr), hex(res), hex(data)))
    
    def i2cread(self):
        res = self.i2c_bus.read_i2c_block_data(self.i2c_addr, 0x32, 1)[0]
        return res


##################################################################################
#   This class represents the EEPROM found on the DDIMM chip.                    #
#   It contains useful information about the firmware of the chip.               #
##################################################################################
class Eeprom:
    def __init__(self, i2c_bus_num):
        self.i2c_bus = init_bus(i2c_bus_num)

    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return EEPROM_I2C_ADDR in alive_addresses
    
    def i2cwrite(self, reg_addr, data):
        data = list(reg_addr.to_bytes(2, "big")) + data
        msg = smbus.i2c_msg.write(EEPROM_I2C_ADDR, data)

        try:
            self.i2c_bus.i2c_rdwr(msg)
            return
        except OSError as e:
            if e.errno == 121: # Remote I/O error aka slave NAK
                pass

        sleep(0.005)
        self.i2c_bus.i2c_rdwr(msg)

    def i2cread(self, reg_addr, length=1):
        self.i2cwrite(reg_addr, [])
        msg = smbus.i2c_msg.read(EEPROM_I2C_ADDR, length)
        self.i2c_bus.i2c_rdwr(msg)
        data = list(msg)
        return data[0]
    
    def read_regs(self):
        res = []
        for reg in range(0, 16):
            data = self.i2cread(reg)
            res.append(data)
        odata = int(''.join(format(val, '02x') for val in res[:]), 16)
        print("First Bytes {:#010x}...".format(odata))
        return res
    
    def get_info(self):        
        """read Memory Size"""
        data = self.i2cread(0x4)
        memory_size = 0
        if data == 0x85: memory_size = 32
        elif data == 0x86: memory_size = 64
        print("Memory Size : {}GB".format(memory_size))
        
        """read vendor ID"""
        # Bytes 1 changes but is not representing Vendor ID
        data = self.i2cread(0x1)
        vendor = "UNKNOWN"
        if data == 0x9: vendor = "IBM"
        elif data == 0x4: vendor = "SMART"
        else: vendor = "UNKNOW Memory code"
        logging.info("Old Vendor  :" + vendor)
        
        logging.info("bytes 512(0x200), 513(0x201) contain Manuf ID : MICRON = 0x802C, SAMSUNG = 0x80CE, SMART = 0x0194)")
        data = (self.i2cread(512) << 8) + (self.i2cread(513))
        logging.info("Manuf ID: {:#006x}".format(data))
        if data == 0x802C: vendor = "MICRON"
        elif data == 0x80CE: vendor = "SAMSUNG"
        elif data == 0x0194: vendor = "SMART"
        else: vendor = "UNKNOW NEW Memory code" 
        print("Vendor      :",vendor)       

        ddimm_info = (memory_size, vendor)     
        return ddimm_info
    



# --------------------- Helper functions ------------------- #
def open_path(busnum):
    """ Open path from first level mux for second level mux 
        to be visible (not DDIMMs) """
    mux = Mux(MUX2_I2C_ADDR, busnum)
    mux.i2cwrite(0x01)

def close_path(busnum):
    """ Close the first level mux """
    mux = Mux(MUX2_I2C_ADDR, busnum)
    mux.i2cwrite(0x00)

"""Information regarding the I2C commands for the DDIMM PMICs is available in the JEDEC Standard Document JESD301-1A available here: https://www.jedec.org/standards-documents/docs/jesd301-1a"""
""" Ice has a single Power Managment Chip (UPM) and starts by itself"""
def set_pmics(busnum):
    card = scan_bus()
    if card in ["DDIMM"]:
        try:
            pmic1 = Pmic(PMIC1_I2C_ADDR, busnum)
            pmic2 = Pmic(PMIC2_I2C_ADDR, busnum)
            pmic1.i2cwrite(0x80)
            pmic2.i2cwrite(0x80)
            print("Activated DDIMM's both PMICs to provide access to the Explorer chip")
        except:
            print("ERROR !! : DDIMM's PMICS not detected !")
            exit()
    elif card in ["GEMINI"]:
        print("GEMINI Card detected, UPM started by itself")
    else : print("WARNING : unknown card or no card")

def clear_pmics(busnum):
    """ Desactivate PMICs to power off Explorer chip """
    pmic1 = Pmic(PMIC1_I2C_ADDR, busnum)
    pmic2 = Pmic(PMIC2_I2C_ADDR, busnum)
    pmic1.i2cwrite(0x00)
    pmic2.i2cwrite(0x00)

def setup_ddimm_path(ddimm, busnum, verbose):
    """ Open path for given ddimm, only one at a time """
    open_path(busnum)
    mux = Mux(MUX3_I2C_ADDR, busnum)
    if ddimm.lower() == "none":
        mux.i2cwrite(0x00)
    elif 'a' in ddimm.lower():
        mux.i2cwrite(1 << DDIMMA)
        #set_pmics(busnum, verbose)
    elif 'b' in ddimm.lower():
        mux.i2cwrite(1 << DDIMMB)
        #set_pmics(busnum, verbose)

def path_status(busnum):
    """ Get current path status (which DDIMM is accessible) """
    mux1 = Mux(MUX2_I2C_ADDR, busnum)
    if mux1.i2cread() == 0x0: print("I2C Path is not connected to any DDIMM port.")
    if mux1.i2cread() == 0x1:
        mux2 = Mux(MUX3_I2C_ADDR, busnum)
        if mux2.i2cread() == 0x0: print("No I2C path is open for any DDIMM")
        elif mux2.i2cread() == 0x1: print("I2C Path is set to PORT 0/A")
        elif mux2.i2cread() == 0x2: print("I2C Path is set to PORT 1/B")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    pass