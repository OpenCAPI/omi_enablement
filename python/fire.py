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

##################################################################################
#    This class represents the Fire design that generates traffic and checks     #
#    results in regard to OCMBs.                                                 #
#    The methods on this class give the possibility to interrogate the design    #
#    in the FPGA through the I2C bus.                                            #
##################################################################################

class Fire:

    """ 
        Initialize i2c bus and get the ID and frequency of Fire 
        """
    def __init__(self, i2c_bus_num=3):
        self.i2c_bus_num = i2c_bus_num
        self.i2c_bus = init_bus(i2c_bus_num)
        self.id, self.is_dirty = self.get_id()
        if self.id & 0x0fffffff == FIRE_400_MHZ_VERSION_ID: self.freq = 400
        else : self.freq = 333
    
    """ 
        Detect if Fire's i2c address is visible on the bus 
        """
    def detect(self):
        alive_addresses = get_alive_addresses(self.i2c_bus)
        return FIRE_I2C_ADDR in alive_addresses
    
    """
        Read a Fire's register value.
        The operation will write a 8 bytes value representing the register address to read its value, 
        followed by 8 reads of 1 byte each that form the register content.
        Both the I2C operations are done without providing any register addresses. 
        The hardware automatically puts the result in a FIFO tied directly to I2C bus.
        """
    def i2cread(self, reg_addr):
        msg = smbus.i2c_msg.write(FIRE_I2C_ADDR, list(reg_addr.to_bytes(8, 'big')))
        self.i2c_bus.i2c_rdwr(msg)
        
        block = []
        for i in range(8):
            d = self.i2c_bus.read_byte(FIRE_I2C_ADDR)
            block.append(d)

        # format result
        odata = int(''.join(format(val, '02x') for val in block), 16)
        logging.info("Reading {} from {}".format(hex(odata), hex(reg_addr)))
        
        return odata
    
    """
        Write data in a Fire's register.
        The operation will write a 16 bytes value representing the register address
        to modify its value (8 bytes) + the data to write (8 bytes).
        It also checks if the write operation has succeeded or not.
        """
    def i2cwrite(self, reg_addr, data):
        new_data = list(reg_addr.to_bytes(8, 'big')) + list(data.to_bytes(8, 'big'))

        msg = smbus.i2c_msg.write(FIRE_I2C_ADDR, new_data)
        self.i2c_bus.i2c_rdwr(msg)
        logging.info("Writing {:#010x} into {:#010x}".format(data, reg_addr))
        
        r_data = self.i2cread(reg_addr)
        return (r_data == data)
    
    """
        Get the ID of FIRE and check the Dirty bit. 
        It's the operation of reading the content value of FIRE_FML_FIRE_VERSION_REG register.
        """
    def get_id(self):
        id = self.i2cread(FIRE_FML_FIRE_VERSION_REG)
        is_dirty = (id & FIRE_ID_DIRTY_BIT) >> 28
        logging.info('{:#010x} {}'.format(id, "Dirty" if is_dirty else ""))
        return id, is_dirty

    """
        Make provided DDIMM(s) enter Reset State.
        RESET STATE = ON
        """
    def set_ddimm_on_reset(self, ddimm):
        val = self.i2cread(FIRE_FML_RESET_CONTROL_REG)
        if 'a' in ddimm.lower(): val = val & ~FIRE_FML_DDIMMA_RESET_BIT
        if 'b' in ddimm.lower(): val = val & ~FIRE_FML_DDIMMB_RESET_BIT
        if 'c' in ddimm.lower(): val = val & ~FIRE_FML_DDIMMC_RESET_BIT
        if 'd' in ddimm.lower(): val = val & ~FIRE_FML_DDIMMD_RESET_BIT
        if 'w' in ddimm.lower(): val = val & ~FIRE_FML_DDIMMW_RESET_BIT
        self.i2cwrite(FIRE_FML_RESET_CONTROL_REG, val)
    
    """
        Make provided DDIMM(s) quit Reset State.
        RESET STATE = OFF
        """
    def set_ddimm_off_reset(self, ddimm):
        val = self.i2cread(FIRE_FML_RESET_CONTROL_REG)
        if 'a' in ddimm.lower(): val = val | FIRE_FML_DDIMMA_RESET_BIT
        if 'b' in ddimm.lower(): val = val | FIRE_FML_DDIMMB_RESET_BIT
        if 'c' in ddimm.lower(): val = val | FIRE_FML_DDIMMC_RESET_BIT
        if 'd' in ddimm.lower(): val = val | FIRE_FML_DDIMMD_RESET_BIT
        if 'w' in ddimm.lower(): val = val | FIRE_FML_DDIMMW_RESET_BIT
        self.i2cwrite(FIRE_FML_RESET_CONTROL_REG, val)

    """ 
        Start the sync/training on the fire side. it expects ddimm's letter to 
        train as an argument.
        This should be preceeded by an Explorer's sync/training procedure for the 
        complete training.
        """
    def sync(self, ddimm):
        # Done after explorer.sync()
        if 'a' in ddimm.lower():
            self.i2cread(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10)
            self.i2cwrite(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045)
            self.i2cwrite(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045)
        if 'b' in ddimm.lower():
            self.i2cread(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10)
            self.i2cwrite(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045)
            self.i2cwrite(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045)

    """
        This function checks if the training is done from the Fire side.
        It should be executed AFTER executing sync/training program on the 
        Explorer's sode followed by Fire's side, thus after a complete training.
        """
    def check_sync(self, ddimm, verbose=0):
        for i in range (0, len(ddimm)):
            if ddimm[i].lower() == 'a': reg = FIRE_DDIMMA_HOST_CONF_STATUS_REG
            elif ddimm[i].lower() == 'b': reg = FIRE_DDIMMB_HOST_CONF_STATUS_REG
            
            if self.i2cread(reg) & (1 << 3): 
                if verbose: print("DDIMM{} is in sync".format(ddimm[i].upper()))
                else: return 1
            else : 
                if verbose: print("DDIMM{} is NOT in sync".format(ddimm[i].upper()))
                else: return 0
            
    def retrain(self, ddimm, verbose=0):
        for i in range (0, len(ddimm)):
            if ddimm[i].lower() == 'a': 
                reg = FIRE_DDIMMA_OPENCAPI_DL_CONTROL
                check_reg = FIRE_DDIMMA_HOST_CONF_STATUS_REG
            elif ddimm[i].lower() == 'b': 
                reg = FIRE_DDIMMB_OPENCAPI_DL_CONTROL
                check_reg = FIRE_DDIMMB_HOST_CONF_STATUS_REG

            val = self.i2cread(reg)
            self.i2cwrite(reg, (val | (1 << 24)))

            
            if self.i2cread(check_reg) & (1 << 3): 
                if verbose: print("DDIMM{} is in sync".format(ddimm[i].upper()))
                else: return 1
            else : 
                if verbose: print("DDIMM{} is NOT in sync".format(ddimm[i].upper()))
                else: return 0
            
        

if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)

    fire = Fire()
