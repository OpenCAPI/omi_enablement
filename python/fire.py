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

from re import I
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
	def __init__(self, i2c_bus_num, freq=333):
		self.i2c_bus_num = i2c_bus_num
		self.i2c_bus = init_bus(i2c_bus_num)
		self.id, self.is_dirty, self.freq_def = self.get_id()
		#print(self.freq_def)
		#logging.info('{:#03x} {}'.format(self.freq_def))
		#logging.info("freq_def =", self.freq_def)
		if (self.freq_def == 0):
			print("WARNING: Old version of code used, doesn't contain OMI link speed")
			logging.info("         trying to find an old correspondence")
			if self.id & 0x0fffffff in FIRE_400_MHZ_VERSION_ID: self.freq = 400; logging.info("Freq set to 400MHz")
			elif self.id & 0x0fffffff in FIRE_333_MHZ_VERSION_ID: self.freq = 333; logging.info("Freq set to 333MHz")
			else:
				print("Couldn't find corresponding frequency to this Fire version, continuing with %3dMHz" %(freq))
				self.freq = freq
=======
    """ 
        Initialize i2c bus and get the ID and frequency of Fire 
        """
    def __init__(self, i2c_bus_num, freq=333):
        self.i2c_bus_num = i2c_bus_num
        self.i2c_bus = init_bus(i2c_bus_num)
        self.id, self.is_dirty = self.get_id()
        if self.id & 0x0fffffff in FIRE_400_MHZ_VERSION_ID: self.freq = 400
        elif self.id & 0x0fffffff in FIRE_333_MHZ_VERSION_ID: self.freq = 333
        else: 
            printf("Couldn't find corresponding frequency to this Fire version, continuing with {}MHz", freq)
            self.freq = freq
    
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
            
        
		elif (self.freq_def == 0x001): self.freq = 333
		elif (self.freq_def == 0x010): self.freq = 366
		elif (self.freq_def == 0x011): self.freq = 400
		else: print("WARNING: No proper frequency setting found")
		
	
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
		logging.info("Fire Reading {} from {}".format(hex(odata), hex(reg_addr)))
		
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
		logging.info("Fire Writing {:#010x} into {:#010x}".format(data, reg_addr))
		
		r_data = self.i2cread(reg_addr)
		return (r_data == data)
	
	"""
		Get the ID of FIRE and check the Dirty bit. 
		It's the operation of reading the content value of FIRE_FML_FIRE_VERSION_REG register.
		"""
	def get_id(self):
		id = self.i2cread(FIRE_FML_FIRE_VERSION_REG)
		is_dirty = (id & FIRE_ID_DIRTY_BIT) >> 28
		freq_def = (id & FIRE_ID_FREQ_DEF) >> 29
		#print(hex(FIRE_ID_FREQ_DEF))
		#print(freq_def)
		logging.info('{:#010x} {}'.format(id, "Dirty" if is_dirty else ""))
		return id, is_dirty, freq_def

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
		#("----------      : Fire     OMI Training Sequence ------------")
		# Done after explorer.sync()
		if 'a' in ddimm.lower():
			self.i2cread(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10)
			self.i2cwrite(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045)
			self.i2cwrite(FIRE_DDIMMA_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045)
		if 'b' in ddimm.lower():
			self.i2cread(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10)
			self.i2cwrite(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004010045)
			self.i2cwrite(FIRE_DDIMMB_HOST_CONF_BASE_ADDR + 0x10, 0x0000000004080045)
		logging.info("---------- End of SEQ4                           ------------")
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


	steps2122 = ('steps2122',
		'R',	0x2001000000000000	,0x06361014	,"",
		'W',	0x2001000000000224	,0x00000221	,"",
		'W',	0x200100000000026c	,0x0000000f	,"",
		'W',	0x2001000000000268	,0x00000000	,"",
		'R',	0x200100000000021c	,0x00000493	,"",
		'R',	0x200100000000024C	,0x00000000	,"",
		'R',	0x2001000000000248	,0x00000000	,"",
		'W',	0x2001000000000210	,0x03010000	,"",
		'W',	0x2001000000010014	,0x00000800	,"",
		'R',	0x2001000000010004	,0x00100000	,"",
		'W',	0x2001000000010004	,0x00100002	,"",

		'W',	0x3001000140092080	,0x0000000000000000	,"",
		'W',	0x3001000140092088	,0x0000000000000001	,"",
		'W',	0x3001000140092090	,0x0000000000000002	,"",
		'W',	0x3001000140092098	,0x0000000000000003	,"",
		'R',	0x3001000140092068	,0x0000000000000000	,"",
		'W',	0x3001000140092068	,0x0000000000000123	,"", 

		'R',	0x2001000000010514	,0x80000000	,"",
		'W',	0x2001000000010514	,0xC0000000	,"",

		'R',	0x2001000000010510	,0x00000000	,"",
		'W',	0x2001000000010510	,0x00000000	,"",
		'R',	0x2001000000010518	,0x00000001	,"",
		'W',	0x2001000000010518	,0x00010001	,"",
		'R',	0x200100000001030C	,0x00000000	,"",
		'W',	0x200100000001030C	,0x00000001	,"",
									
		'R',	0x3001000140084380	,0x0000000000000000	,"",
	
		'R',	0x200100000001050C	,0x00000000	,"",
		'W',	0x200100000001050C	,0x01000000	,"",
										
										
		'R',	0x30010001400843B0	,0x0000000000000000	,"",
		'R',	0x30010001400843B8	,0x0000000000000000	,"",
		'R',	0x3001000140092030	,0x0000000000000000	,"",
		'R',	0x3001000140092038	,0x0000000000000000	,"",
		'R',	0x3001000140200080	,0x0000000000000000	,"",
		'R',	0x3001000140200088	,0x0000000000000000	,"",
		'R',	0x3001000140094030	,0x0000000000000000	,"",
		'R',	0x3001000140094038	,0x0000000000000000	,"",
		'R',	0x30010001402000B8	,0x0000000000000000	,"",
		'W',	0x30010001402000B8	,0x0000000000000000	,"",
		'W',	0x30010001400843B0	,0x0000000000000000	,"",
		'W',	0x30010001400843B8	,0x2200000000000000	,"",
		'W',	0x30010001400843A0	,0xC1FFFFFFFFFFFFFF	,"",
		'W',	0x3001000140092030	,0x0000000000000000	,"",
		'W',	0x3001000140092038	,0x0068102000000000	,"",
		'W',	0x3001000140092020	,0xFF07C01FFFFFFFFF	,"",
		'W',	0x3001000140200080	,0x0000000000000000	,"",
		'W',	0x3001000140200088	,0xE080010000000001	,"",
		'W',	0x3001000140200070	,0x1F7FFEFFFFFFFFFE	,"",
		'W',	0x3001000140094030	,0x0000000000000000	,"",
		'W',	0x3001000140094038	,0x3200000000000000	,"",
		'W',	0x3001000140094020	,0xCDFFFFFFFFFFFFFF	,"",
		'R',	0x30010001400920A0	,0x0000000000000000	,"",
		'W',	0x30010001400920A0	,0x0080000000000062	,"",
		'R',	0x30010001400920A8	,0x0000000000000000	,"",
		'W',	0x30010001400920A8	,0x0000000002000000	,"",
		'R',	0x3001000140092068	,0x0000000000000000	,"",
		'W',	0x3001000140092068	,0x0200000000000000	,"",

		'W',	0x010400000000000C	,0x00000800,"",

		'W',	0x3001000140084738	,0x8000000000000000 ,"", 
		'W',	0x2001000100002058	,0x0000000000000001 ,"",
		'W',	0x000000010103FF40	,0x0000000042410007 ,"",
		'W',	0x300100010103FF48	,0x00000000FFFFFFFF ,"",
		'W',	0x300100010103FF50	,0x0000000000000000 ,"",
		'W',	0x300100010103FF58	,0x0000000000000000 ,"",
		'W',	0x300100010103FF60	,0x0000000000000000 ,"",
		'W',	0x300100010103FF68	,0x0000000000000000 ,"",
		'W',	0x300100010103FF70	,0x0000000000000000 ,"",
		'W',	0x300100010103FF78	,0x3932F90100000000 ,"",
		'W',	0x3001000140084730	,0x8000000000000000 ,"",
		'R',	0x2001000100002058	,0x0000000000000001 ,"",
		)
		  
	steps25_a0 = ("steps25_a0",
		'W'	,0x3001000140084738		,0x8000000000000000	,"",			
		'W'	,0x2001000100002058		,0x0000000000000001	,"",

		'R'	,0x300100014008A1C0	,0x4210000000000000	,"",
		'W'	,0x300100014008A1C0	,0x4210000000000000	,"",

		'R'	,0x300100014008A060	,0x18B0056072A315AC	,"",
		'W'	,0x300100014008A060	,0x046005604394A5AC	,"",
		'R'	,0x300100014008A068	,0xC448C44894A4CC30	,"",
		'W'	,0x300100014008A068	,0x844794476318ED34	,"",

		'R'	,0x300100014008A070	,0x8810B5B4002CC480	,"",
		'W'	,0x300100014008A070	,0x780E9CEB002AA478	,"",
		'R'	,0x300100014008A078	,0x79FFE0001BF7FD50	,"",
		'W'	,0x300100014008A078	,0x79FFE0001BF7FD10	,"",
		'R'	,0x300100014008A080	,0xFC00084000000052	,"",
		'W'	,0x300100014008A080	,0xFC08084000000043	,"",

		'R'	,0x300100014008A088	,0x0000000000000000	,"",
		'W'	,0x300100014008A088	,0x5FF4200040800064	,"",
		'R'	,0x300100014008A0A8	,0x0000148082002B0C	,"",
		'W'	,0x300100014008A0A8	,0x000008808200430C	,"",
		'R'	,0x300100014008A0B0	,0x11635F11635F0500	,"",
		'W'	,0x300100014008A0B0	,0x1161161161160500	,"",

		'R'	,0x300100014008A0B8	,0x4848121284842121	,"",
	)

	steps25_a1_IBM = ("steps25_a1_IBM",
		'W'	,0x300100014008A0B8	,0x5A0000005A000000	,"IBM",
		)

	steps25_a1_SMART = ("steps25_a1_SMART",
		'W'	,0x300100014008A0B8	,0x0000005A000000	,"SMART",
		)		

	steps25_a2 = ("steps25_a2",
		'R'	,0x300100014008A0C8	,0x0010100010080000	,"",
		'W'	,0x300100014008A0C8	,0x0100100010080000	,"",
		'R'	,0x300100014008A0D0	,0x0400000000000000	,"",
		'W'	,0x300100014008A0D0	,0x0800000000000000	,"",
		'R'	,0x300100014008A1A0	,0x0330C00230300D68	,"",
	)

	steps25_a3_32 = ("steps25_a3_32",
		'W'	,0x300100014008A1A0	,0x00282001D3281810	,"32G",
	)
	steps25_a3_64 = ("steps25_a3_64",
		'W'	,0x300100014008A1A0	,0x00282001D33DD810	,"64G",
	)

	steps25_a4 = ("steps25_a4",
		'R'	,0x300100014008A1B0	,0x0148400202102D00	,"",
		'W'	,0x300100014008A1B0	,0x0107380202102D00	,"",
		'R'	,0x300100014008A1B8	,0x0084C21000000001	,"",
		'W'	,0x300100014008A1B8	,0x008435B00000A083	,"",

		'R'	,0x300100014008C378	,0x0000000000000000	,"",
		)
	steps25_a5_32 = ("steps25_a5_32",
		'W'	,0x300100014008C378	,0x820640003DE63DCD	,"32G",
		'R'	,0x300100014008C380	,0x0000000000000000	,"",
		'W'	,0x300100014008C380	,0x100F00002708090A	,"32G",
		)
	steps25_a5_64 = ("steps25_a5_64",
		'W'	,0x300100014008C378	,0x8207400042063DCD	,"64G",
		'R'	,0x300100014008C380	,0x0000000000000000	,"",
		'W'	,0x300100014008C380	,0x111000002708090A	,"64G",
		)			
	steps25_a6 = ("steps25_a6",
		'R'	,0x300100014008C388	,0x0000000000000000	,"",
		'W'	,0x300100014008C388	,0x0B0C050400030200	,"",

		'R'	,0x300100014008E168	,0x0813FE3800F00000	,"",
		'W'	,0x300100014008E168	,0x0833FE3800F00000	,"",

		'R'	,0x300100014008A1B0	,0x0107380202102D00	,"",
		'W'	,0x300100014008A1B0	,0x0107380202102D00	,"",
		'R'	,0x300100014008A1B8	,0x008435B00000A083	,"",
		'W'	,0x300100014008A1B8	,0x008435B00000A083	,"",

		'R'	,0x300100014008A0C0	,0x0000000000002000	,"",
		'W'	,0x300100014008A0C0	,0x0100010010002400	,"",
		'R'	,0x300100014008A0C8	,0x0100100010080000	,"",
		'W'	,0x300100014008A0C8	,0x0100100008020000	,"",

		'R'	,0x300100014008A030	,0x0000000000000000	,"",
		'R'	,0x300100014008A038	,0x0000000000000000	,"",
		'R'	,0x3001000140200080	,0x0000000000000000	,"",
		'W'	,0x3001000140200088	,0xFFFFFFFFFFFFFFFF	,"",

		'W'	,0x300100014008A030	,0x0000000000000000	,"",
		'W'	,0x300100014008A038	,0x8003040000000000	,"",
		'W'	,0x300100014008A020	,0x3FEC31FFFFFFFFFF	,"",
		'W'	,0x3001000140200080	,0x0000000000000000	,"",
		'W'	,0x3001000140200088	,0xFFFFFFFFFFFFFFFF	,"",
		'W'	,0x3001000140200070	,0xFFFFFFFFF3FFFFFF	,"",

		'R'	,0x300100014008A0A8	,0x000008808200430C	,"",
		'W'	,0x300100014008A0A8	,0x000008808200434C	,"",


	)
	steps25_a7_32 = ("steps25_a7_32",
		'W'	,0x300100010102FF00	,0x0003000000000003	,"",
		'W'	,0x300100010102FF08	,0xF3FF03DF00000004	,"",
		'W'	,0x300100010102FF10	,0x0011000A0000000F	,"",
	)
	steps25_a7_64 = ("steps25_a7_64",
		'W'	,0x300100010102FF00	,0x0003000000000003	,"",
		'W'	,0x300100010102FF08	,0xF3FF03DF00000004	,"",
		'W'	,0x300100010102FF10	,0x0012000A0002000F	,"",
	)
	steps25_a8 = ("steps25_a8",
		'W'	,0x300100010102FF18	,0x000035B60002FFF8	,"",
		'W'	,0x300100010102FF20	,0x0000000000000000	,"",
		'W'	,0x300100010102FF28	,0x0030053500010000	,"",
		'W'	,0x300100010102FF30	,0x0014000F001C0022	,"",
		'W'	,0x300100010102FF38	,0x0078000D0014000C	,"",
	)
	steps25_a9_IBM = ("steps25_a9_IBM",
		'W'	,0x300100010102FF40	,0x0000000000220022	,"",
		'W'	,0x300100010102FF48	,0x0000000000780078	,"",
		'W'	,0x300100010102FF50	,0x0000000000000000	,"",
		'W'	,0x300100010102FF58	,0x0000000000000022	,"",
		'W'	,0x300100010102FF60	,0x0012001200690019	,"",
		'W'	,0x300100010102FF68	,0x0000000000000000	,"",
		'W'	,0x300100010102FF70	,0x0000000000000000	,"",
		'W'	,0x300100010102FF78	,0x0808080A00060000	,"",
		'W'	,0x300100010102FF80	,0x0707070A08080808	,"",
		'W'	,0x300100010102FF88	,0x0000000007070707	,"",
		'W'	,0x300100010102FF90	,0x0000000000000000	,"",
	)
	steps25_a9_SMART = ("steps25_a9_SMART",
		'W'	,0x300100010102FF40	,0x00000000003C003C	,"",
		'W'	,0x300100010102FF48	,0x0000000000500050	,"",
		'W'	,0x300100010102FF50	,0x0000000000220022	,"",
		'W'	,0x300100010102FF58	,0x0000000000000022	,"",
		'W'	,0x300100010102FF60	,0x00000012005C0022	,"",
		'W'	,0x300100010102FF68	,0x0000000000000000	,"",
		'W'	,0x300100010102FF70	,0x0000000000000000	,"",
		'W'	,0x300100010102FF78	,0x0404040600060000	,"",
		'W'	,0x300100010102FF80	,0x0606060804040404	,"",
		'W'	,0x300100010102FF88	,0x0000000006060606	,"",
		'W'	,0x300100010102FF90	,0x0000000000000000	,"",
	)

	steps25_a10 = ("steps25_a10",
		'W'	,0x3001000140084738	,0x8000000000000000	,"",
		'W'	,0x2001000100002058	,0x0000000000000001	,"",
	)

	steps25_a11_IBM_32 = ("steps25_a11_IBM_32",
		'W'	,0x300100010103FF40	,0x0000009342430102	,"",
		'W'	,0x300100010103FF48	,0x00000000CE766AE8	,"",
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",
		'W'	,0x300100010103FF60	,0x0000000000000003	,"",
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",
		'W'	,0x300100010103FF78	,0x62A8E3AC00000000	,"",

		'W'	,0x3001000140084730	,0x8000000000000000	,"",
		'R'	,0x2001000100002058	,0x0000000000000001	,"",
		) 

	steps25_a11_IBM_64 = ("steps25_a11_IBM_64",
		'W'	,0x300100010103FF40	,0x0000009342430102	,"",
		'W'	,0x300100010103FF48	,0x0000000034F60CD5	,"",
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",
		'W'	,0x300100010103FF60	,0x0000000000000003	,"",
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",
		'W'	,0x300100010103FF78	,0x4605564200000000	,"",

		'W'	,0x3001000140084730	,0x8000000000000000	,"",
		'R'	,0x2001000100002058	,0x0000000000000001	,"",
		)

	steps25_a11_SMART_32 = ("steps25_a11_SMART_32",
		'W'	,0x300100010103FF40	,0x0000009342430102	,"",
		'W'	,0x300100010103FF48	,0x000000004E036F9F	,"",
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",
		'W'	,0x300100010103FF60	,0x0000000000000003	,"",
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",
		'W'	,0x300100010103FF78	,0x0BB9E97D00000000	,"",

		'W'	,0x3001000140084730	,0x8000000000000000	,"",
		'R'	,0x2001000100002058	,0x0000000000000001	,"",
		)

	steps25_a11_SMART_64 = ("steps25_a11_SMART_64",
		'W'	,0x300100010103FF40	,0x0000009342430102	,"",
		'W'	,0x300100010103FF48	,0x00000000B48309A2	,"",
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",
		'W'	,0x300100010103FF60	,0x0000000000000003	,"",
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",
		'W'	,0x300100010103FF78	,0x2F145C9300000000	,"",

		'W'	,0x3001000140084730	,0x8000000000000000	,"",
		'R'	,0x2001000100002058	,0x0000000000000001	,"",
		)
		
	""" Poll for response ready done in omi.py """

	steps25_b = ("steps25_b",
		'R'	,0x2001000100002058	,0x0000000000000001	,"",
		'R'	,0x300100010103FF00	,0x0000000042430002	,"",
		'R'	,0x300100010103FF08	,0x0000000000000000	,"",
		'R'	,0x300100010103FF10	,0x0000000000000000	,"",
		'R'	,0x300100010103FF18	,0x0000000000000000	,"",
		'R'	,0x300100010103FF20	,0x0000000000000000	,"",
		'R'	,0x300100010103FF28	,0x0000000000000000	,"",
		'R'	,0x300100010103FF30	,0x0000000000000000	,"",
		'R'	,0x300100010103FF38	,0x27941C5A00000000	,"",
		'W'	,0x2001000100002058	,0x0000000000000001	,"",
		)

	"""	steps26_a = ("steps26_a",
		'W'	,0x3001000140084738	,0x8000000000000000	,"",			
		'W'	,0x2001000100002058	,0x0000000000000001	,"",			

		'W'	,0x300100010102FF00	,0x0003000000000003	,"",			
		'W'	,0x300100010102FF08	,0xF3FF03DF00000004	,"",			
		'W'	,0x300100010102FF10	,0x0011000A0000000F	,"",			
		'W'	,0x300100010102FF18	,0x000035B60002FFF8	,"",			
		'W'	,0x300100010102FF20	,0x0000000000000000	,"",			
		'W'	,0x300100010102FF28	,0x0030053500010000	,"",			
		'W'	,0x300100010102FF30	,0x0014000F001C0022	,"",			
		'W'	,0x300100010102FF38	,0x0078000D0014000C	,"",			
		'W'	,0x300100010102FF40	,0x0000000000220022	,"",			
		'W'	,0x300100010102FF48	,0x0000000000780078	,"",			
		'W'	,0x300100010102FF50	,0x0000000000000000	,"",			
		'W'	,0x300100010102FF58	,0x0000000000000022	,"",			
		'W'	,0x300100010102FF60	,0x0012001200690019	,"",			
		'W'	,0x300100010102FF68	,0x0000000000000000	,"",			
		'W'	,0x300100010102FF70	,0x0000000000000000	,"",			
		'W'	,0x300100010102FF78	,0x0808080A00060000	,"",			
		'W'	,0x300100010102FF80	,0x0707070A08080808	,"",			
		'W'	,0x300100010102FF88	,0x0000000007070707	,"",			
		'W'	,0x300100010102FF90	,0x0000000000000000	,"","""

	step26_a0_32 = steps25_a7_32
	step26_a0_64 = steps25_a7_64
	step26_a1 = steps25_a8
	step26_a2_IBM = steps25_a9_IBM
	step26_a2_SMART = steps25_a9_SMART

	steps26_a3 = ("steps26_a3",
		'W'	,0x3001000140084738	,0x8000000000000000	,"",
		'W'	,0x2001000100002058	,0x0000000000000001	,"",
	)

	steps26_a4_IBM_32 = ("steps26_a4_IBM_32",
		'W'	,0x300100010103FF40	,0x0000009342440102	,"",			
		'W'	,0x300100010103FF48	,0x00000000CE766AE8	,"",			
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF60	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF78	,0x821B296600000000	,"",
		'W'	,0x3001000140084730	,0x8000000000000000	,"",
	)
	steps26_a4_IBM_64 = ("steps26_a4_IBM_64",
		'W'	,0x300100010103FF40	,0x0000009342440102	,"",			
		'W'	,0x300100010103FF48	,0x0000000034F60CD5	,"",			
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF60	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF78	,0xA6B69C8800000000	,"",
		'W'	,0x3001000140084730	,0x8000000000000000	,"",
	)
	steps26_a4_SMART_32 = ("steps26_a4_SMART_32",
		'W'	,0x300100010103FF40	,0x0000009342440102	,"",			
		'W'	,0x300100010103FF48	,0x000000004E036F9F	,"",			
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF60	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF78	,0xEB0A23B700000000	,"",
		'W'	,0x3001000140084730	,0x8000000000000000	,"",
	)
	steps26_a4_SMART_64 = ("steps26_a4_SMART_64",
		'W'	,0x300100010103FF40	,0x0000009342440102	,"",			
		'W'	,0x300100010103FF48	,0x00000000B48309A2	,"",			
		'W'	,0x300100010103FF50	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF58	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF60	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF68	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF70	,0x0000000000000000	,"",			
		'W'	,0x300100010103FF78	,0xCFA7965900000000	,"",
		'W'	,0x3001000140084730	,0x8000000000000000	,"",
	)

	""" Poll for response ready done in omi.py """ 

	steps_26b0 = ("steps_26b0",
		'R'	,0x2001000100002058		,0x0000000000000001	,"",			
										
		'R'	,0x300100010103FF00	,0x0000021042440102	,"",			
		'R'	,0x300100010103FF08	,'XXXXXXXXXXXXXXXXX',"0x00000000335730B2",			
		'R'	,0x300100010103FF10	,0x0000000000000000	,"",
		'R'	,0x300100010103FF18	,0x0000000000000000	,"",	
		'R'	,0x300100010103FF20	,0x0000000000000000	,"",		
		'R'	,0x300100010103FF28	,0x0000000000000000	,"",		
		'R'	,0x300100010103FF30	,0x0000000000000000	,"",		
		'R'	,0x300100010103FF38	,'XXXXXXXXXXXXXXXXX',"0x17E088B300000000",		

		'W'	,0x2001000100002058		,0x0000000000000001	,"",
											
		'R'	,0x300100014008C538		,0x00FFFF0000001000	,"",
		'W'	,0x300100014008C538		,0x00FFFF8000001000	,"",
											
		'R'	,0x300100014008A1B0		,0x0107380202102D00	,"",
		'W'	,0x300100014008A1B0		,0x0107380202302D00	,"",
		'R'	,0x300100014008C528		,0x0000000000000000	,"",
		'W'	,0x300100014008C528		,0x4000000000000000	,"",
		'R'	,0x300100014008C530		,0x0000000000000000	,"",
		'W'	,0x300100014008C0A8		,0x000008F0CC000000	,"",
		'W'	,0x300100014008C1A8		,0x02EE000000000001	,"",
	)

	steps_26b1_IBM = ("steps_26b1_IBM",
		'W'	,0x300100014008C0B0		,0x0D4028F044000000	,"",
		'W'	,0x300100014008C1B0		,0x0018000000000002	,"",
		'W'	,0x300100014008C0B8		,0x0D4028F088000000	,"",
	)
	steps_26b1_SMART = ("steps_26b1_SMART",
		'W'	,0x300100014008C0B0		,0x0D1028F044000000	,"",
		'W'	,0x300100014008C1B0		,0x0018000000000002	,"",
		'W'	,0x300100014008C0B8		,0x128448F088000000	,"",
	)
	steps_26b2 = ("steps_26b2",
		'W'	,0x300100014008C1B8		,0x0018000000000003	,"",
		'W'	,0x300100014008C0C0		,0x000008F0CC000000	,"",
		'W'	,0x300100014008C1C0		,0x0000000000000020	,"",

		'R'	,0x300100014008C528		,0x0000000000000000	,"",
		'W'	,0x300100014008C528		,0x8000000000000000	,"",
		'R'	,0x300100014008C530		,0x4000000000000000	,"",
		'R'	,0x300100014008A1B0		,0x0107380202302D00	,"",
		'W'	,0x300100014008A1B0		,0x0107380202102D00	,"",
												
		'R'	,0x300100014008C030		,0x0000000000000000	,"",
		'R'	,0x300100014008C038		,0x0000000000000000	,"",
		'R'	,0x300100014008A030		,0x0000000000000000	,"",
		'R'	,0x300100014008A038		,0x8003040000000000	,"",
		'R'	,0x2001000104340000		,0x0000000000000001	,"",
		'W'	,0x2001000104340000		,0x0000000000000000	,"",

		'R'	,0x200100010408016C		,0x0000000000007429	,"",
		'W'	,0x200100010408016C		,0x0000000000005429	,"",

		'R'	,0x2001000104340000		,0x0000000000000000	,"",
		'W'	,0x2001000104340000		,0x0000000000000001	,"",
											
		'W'	,0x300100014008C030		,0x0000000000000000	,"",
		'W'	,0x300100014008C038		,0x4004000000000000	,"",
		'W'	,0x300100014008A030		,0x0000000000000000	,"",
		'W'	,0x300100014008A038		,0x8443050800000000	,"",
	)
	steps27_a0 = ("steps27_a0",
		'R'	,0x300100014008A1B0		,0x0107380202102D00	,"",
		'W'	,0x300100014008A1B0		,0x0107380202102D00	,"",
		'R' ,0x300100014008A208		,0x0000000000000000	,"",
		'W'	,0x300100014008A208		,0x0000000000000001	,"",
		'R' ,0x300100014008A0A8		,0x000008808200434C	,"",
		'W'	,0x300100014008A0A8		,0x000088808200434C	,"",
	)
	
	steps27_a1_32 = ("steps27_a1_32",
		'R' ,0x300100014008A1A0		,0x00282001D3281810	,"",
		'W'	,0x300100014008A1A0		,0x80282001D3281810	,"",
		)
	steps27_a1_64 = ("steps27_a1_64",
		'R' ,0x300100014008A1A0		,0x00282001D33DD810	,"",
		'W'	,0x300100014008A1A0		,0x80282001D33DD810	,"",
		)
	steps27_a2 = ("steps27_a2",
		'R' ,0x300100014008A1B8		,0x008435B00000A083	,"",
		'W'	,0x300100014008A1B8		,0x008435B00000A081	,"",
		'R' ,0x300100014008A088		,0x5FF4200040800064	,"",
		'W'	,0x300100014008A088		,0xDFF4200040800064	,"",
		'R' ,0x300100014008A088		,0xDFF4200040800064	,"",
		'W'	,0x300100014008A088		,0xDFF42001C8000080	,"",
		'R' ,0x300100014008E168		,0x0833FE3800F00000	,"",
		'R' ,0x300100014008E140		,0x0000000000000000	,"",
		'W'	,0x300100014008E140		,0x51A8E00000000000	,"",
		'W'	,0x300100014008E168		,0x0833FEBF10700000	,"",
												
		'R' ,0x300100014008C030		,0x0000000000000000	,"",
		'R' ,0x300100014008C038		,0x4004000000000000	,"",
		'R' ,0x300100014008A030		,0x0000000000000000	,"",
		'R' ,0x300100014008A038		,0x8443050800000000	,"",
		'R' ,0x300100014008E030		,0x0000000000000000	,"",
		'W'	,0x300100014008E038		,0x0000000000000000	,"",
		'R' ,0x300100014008E188		,0x0000000000000000	,"",
		'W'	,0x300100014008E188		,0x0000400000000000	,"",
		'W'	,0x300100014008A030		,0x0020000000000000	,"",
		'W'	,0x300100014008A038		,0x4004000000000000	,"",
		'W'	,0x300100014008C020		,0xFFDFFFFFFFFFFFFF	,"",
		'W'	,0x300100014008E030		,0x0000000000000000	,"",
		'W'	,0x300100014008E038		,0x000000005AE60000	,"",
		'W'	,0x300100014008E020		,0xFFFFFFFFA5007FFF	,"",
		'W'	,0x300100014008A030		,0x0000000000000000	,"",
		'W'	,0x300100014008A038		,0xA443050800000000	,"",
		'W'	,0x300100014008A020		,0xDFFFFFFFFFFFFFFF	,"",
	)


	def reg_ops(self, reg_list, _ddimm, _vendor, _size):
		logging.info(_ddimm)
		logging.info(reg_list[0])
		if _ddimm == "a":
			ddimm_add_adj=0x00000000
		elif _ddimm == "b":
			ddimm_add_adj=0x00000400
		else: print("ERROR: incorrect ddimm selection !!")
		logging.info("{:d}".format(len(reg_list)//4) + " registers to be R/W:")
		
		for i in range(1, len(reg_list), 4):
			""" Address is computed with port, based on port0 address """
			reg=reg_list[i+1]+(ddimm_add_adj<<32)
			logging.info("0x{:0>16x}".format(reg))
			
			if reg_list[i] == 'R':
				if  (type(reg_list[i+2])  == str):
					logging.info("READ  REG: " + "0x{:0>16x}".format(reg) + " No expectation")
				else:
					logging.info("READ  REG: " + "0x{:0>16x}".format(reg) + " EXP : " + "0x{:0>16x}".format(reg_list[i+2]) + " READ: "  + "0x{:0>16x}".format(self.i2cread(reg)))
					if ("0x{:0>16x}".format(reg_list[i+2]) != "0x{:0>16x}".format(self.i2cread(reg))):
						print("!!! WARNING: READ DATA Not expected !!!!")
						print("for Register 0x{:0>16x}".format(reg))
			else:
				logging.info("WRITE REG: " + "0x{:0>16x}".format(reg) + " DATA: " + "0x{:0>16x}".format(reg_list[i+2]));self.i2cwrite(reg, reg_list[i+2])

if __name__ == "__main__":
	# logging.basicConfig(level=logging.INFO)
	fire = Fire()
