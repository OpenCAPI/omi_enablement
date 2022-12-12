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

import smbus2 as smbus
import logging

from constants import *

def init_bus(i2c_bus_num=3):
    try:
        return smbus.SMBus(i2c_bus_num)
    except IOError as err:
        print("Error in i2c bus.")
     

def get_alive_addresses(bus):
    addr_found = []
    for _addr in range(1, I2C_ADDR_RANGE):
        try:
            res = bus.write_quick(_addr)
            addr_found.append(_addr)
        except: pass
    return addr_found



def scan_bus(busNum=3, verbose=0):
    bus = init_bus(busNum)
    logging.info('I2C bus is initialized.')
    addr_found = [addr for addr in get_alive_addresses(bus)]
    
    
    # Concerning devices, EXP and ice do not have the same address for ID,
    # so we use a criteria based on power managment chips to define which card is plugged
    # return value will contain the type of card
    ret = "None"
    if len(addr_found) > 0:
        for _addr in addr_found:
            if _addr in [dev['addr'] for dev in known_devices]:
                device = [dev['name'] for dev in known_devices if dev['addr'] == _addr][0]
                if verbose: print("  --{:#02x}: {}".format(_addr, device))
                if   device == "PMIC2":      ret = "DDIMM"  # basic criteria to recognize a card type
                elif device.find("UDC90120A")!=-1: ret = "GEMINI"

            else:
                if verbose:print("  --{:#02x}: Unknown device".format(_addr))

    
    else : print("No devices found on I2C-{} bus".format(busNum))

    return ret