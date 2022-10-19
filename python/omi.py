#
# Copyright 2022 International Business Machines
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

import click
import traceback
from time import sleep

from fire import *
from explorer import *
from ice import *
from components import *
from constants import *
from functions import *
from fbist import *
import csv
import traceback
import signal


revision = "1.2"

@click.group()
@click.option('--log/--no-log', default=False, help='Display more info about the execution of the command.')
def main(log):
    if log : logging.basicConfig(level=logging.INFO)

#########################################################
#                   Providing version                   #
#########################################################
@click.command()
def version():
    "Provides code version"
    print("Version:", revision)
    logging.info\
("\
\nVersion 1.1: adds Firmware update and Fbist features\
\nVersion 1.2: corrects the firmware update routine to reduce time")

main.add_command(version)

#########################################################
#                   Handling CTL C                      #
#########################################################
def handler(signum, frame):
    res = input("\nCtrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)
 
signal.signal(signal.SIGINT, handler)

#########################################################
#                   Scaning the I2C bus                 #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
def scan(_busnum):
    "Scan the I2C bus."
    scan_bus(_busnum)
main.add_command(scan)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def init(_busnum, _freq):
    " Initializes the explorer chip. This must be done before any other operation. "
    fire = Fire(_busnum, _freq)
    explorer = Explorer(fire.freq, _busnum)
    print("----------         : Explorer Initialisation    ------------")
    explorer.init()
    #sleep(5)
main.add_command(init)

#########################################################
#          Providing information on selected chip       #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def info(_chip, _busnum, _freq):
    " Gets chip internal information. "
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        print("ID:", hex(fire.id))
        print("Dirty bit:", fire.is_dirty)
        print("Frequency:", fire.freq_def)
    elif _chip.lower() in ["explorer", "exp", "ice"]:
        explorer = Explorer(fire.freq_def, _busnum)
        eeprom = Eeprom(_busnum)
        try:
            explorer.getinfo()
            explorer.get_firmware_info()
        except:
            print("Error. Please make sure you ran init command first (After a reset and initpath).")
            return

        print("ECID:", explorer.ecid)
        print("Entreprise Mode Status:", explorer.ese_mode_status)
        print("Card ID:", explorer.card_id)
        print("EEPROM data: ", end="")
        eeprom.read_regs()
        eeprom.get_info()
    else:
        print("Chip provided is incorrect.")
main.add_command(info)

#########################################################
#                   Reading Chip Register               #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def read(_register, _chip, _busnum, _freq):
    "Reads from a double internal register."
    _register = int(_register, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        #print(hex(fire.i2cread(_register)))
        print("Rd Fire Addr {:#010x} : {:#018x}".format(_register,fire.i2cread(_register)))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        #print(hex(explorer.i2c_double_read(_register)))
        print("Rd Expl Addr {:#010x} : {:#018x}".format(_register,explorer.i2c_double_read(_register)))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
main.add_command(read)

#########################################################
#             Reading single internal Explorer Reg      #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def readreg(_register, _chip, _busnum, _freq):
    "Reads from a single internal reg (only for explorer)."
    _register = int(_register, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        #print(hex(explorer.i2c_double_read(_register)))
        print("Rd Expl Addr {:#010x} : {:#010x}".format(_register,explorer.i2c_simple_readreg(_register)))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
main.add_command(readreg)

#########################################################
#             Reading Chip Reg with expected Value      #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
@click.option('-e', '--expect', '_expect', type=str, required=False, nargs=1, help='Expected read value')
def readexp(_register, _chip, _busnum, _freq, _expect):
    "Reads from an internal register with expectation."
    _register = int(_register, 16)
    _expect   = int(_expect, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        #print(hex(fire.i2cread(_register)))
        print("Rd Fire Addr {:#010x} : {:#018x}, Expect: {:#018x}".format(_register,fire.i2cread(_register),_expect))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        #print(hex(explorer.i2c_double_read(_register)))
        print("Rd Expl Addr {:#010x} : {:#018x}, Expect: {:#018x}".format(_register,explorer.i2c_double_read(_register), _expect))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
main.add_command(readexp)

#########################################################
#             Reading I2C Register                      #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def i2cread(_register, _chip, _busnum, _freq):
    "Reads from an internal reg."
    _register = int(_register, 16)
    
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        print(hex(fire.i2cread(_register)))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        if _register == 0x2: 
            print(hex(explorer.i2cread(_register)))
        else:
            explorer.i2cwrite(_register)
            print(explorer.i2cread(0x2))     # Reg 02 will provide a check of the previous command, eg 0x1B0005 1B is FW API number, 00 is Command OK, 05 is last reg  
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2cread(_register)))
main.add_command(i2cread)

#########################################################
#                   Reading Chip Register               #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-d', '--data', '_data', type=str, required=True, nargs=1, help='Data value to write to the register (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def write(_register, _data, _chip, _busnum, _freq):
    "Writes to an internal reg."
    _register = int(_register, 16)
    _data = int(_data, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        res = fire.i2cwrite(_register, _data)
        print("Wr Fire Addr {:#010x} : {:#018x}".format(_register, _data))
        print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        res = explorer.i2c_double_write(_register, _data)
        print("Wr Expl Addr {:#010x} : {:#018x}".format(_register, _data))
        print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
    else:
        print("Chip provided is incorrect.")
main.add_command(write)


#########################################################
#             Write single internal Explorer reg        #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-d', '--data', '_data', type=str, required=True, nargs=1, help='Data value to write to the register (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def writereg(_register, _data, _chip, _busnum, _freq):
    "Writes to a single internal reg (only for explorer)"
    _register = int(_register, 16)
    _data = int(_data, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        res = explorer.i2c_simple_writereg(_register, _data)
        print("Wr Expl Addr {:#010x} : {:#010x}".format(_register, _data))
        print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
    else:
        print("Chip provided is incorrect.")
main.add_command(writereg)


#########################################################
#             Writing I2C Register                      #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--data', '_data', type=str, required=True, nargs=1, help='Data value to write to the register (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def i2cwrite(_data, _chip, _busnum, _freq):
    "Writes to an internal register of a program."
    _data = int(_data, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        res = fire.i2cwrite(_data)
        # print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        res = explorer.i2cwrite(_data)
        # print("Writing check : {}".format("Success" if res else "Failed"))
    else:
        print("Chip provided is incorrect.")
    
main.add_command(i2cwrite)

#########################################################
#             Reseting selected DDIMM through Fire      #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to reset. Write the letters of DDIMMs to reset without spaces.
                (Examples: abcdsw, bdw, s)''')
@click.option('-s', '--state', '_state', type=str, required=True, nargs=1, help='on: RESET ON | off: RESET OFF')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def ddimmreset(_ddimm, _state, _busnum, _freq):
    "Sets the reset state of the DDIMMs (In RESET mode : ON | Out RESET mode : OFF)."
    fire = Fire(_busnum, _freq)
    if _state.lower() == "on": fire.set_ddimm_on_reset(_ddimm)
    elif _state.lower() == "off": fire.set_ddimm_off_reset(_ddimm)
    else : print("State provided is not supported.")

main.add_command(ddimmreset)

#########################################################
#                   Selecting DDIMMs Path               #
#########################################################

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMM (only one or none) to setup their path.
                (Examples: a, b none)''')
def initpath(_busnum, _ddimm):
    " Setups I2C path to selected DDIMM. "
    if len(_ddimm) > 1 and _ddimm.lower() != "none":
        print("Please provide a valid ddimm letter (a or b) or none.")
        return
    setup_ddimm_path(_ddimm, _busnum)
    #checkpath(_busnum)
main.add_command(initpath)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
def checkpath(_busnum):
    " Gets the current path configuration. "
    path_status(_busnum)
main.add_command(checkpath)

#########################################################
#                       SYNCING                         #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to check their sync. Write the letters of DDIMMs to reset without spaces.
                (Examples: a, b, ab)''')

@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def checksync(_busnum, _ddimm, _freq):
    " Checks for the training/syncing status of a DDIMM. "
    fire = Fire(_busnum, _freq)
    fire.check_sync(_ddimm, verbose=1)

main.add_command(checksync)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to sync. Write the letters of DDIMMs without spaces.
                (Examples: a, b, ab)''')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def sync(_busnum, _ddimm, _freq):
    " Trains/Syncs the provided DDIMM with Fire. "
    fire = Fire(_busnum, _freq)

    for i in range (0, len(_ddimm)):
        print("Sync DDIMM{}...".format(_ddimm[i].upper()), end=" ")
        if fire.check_sync(_ddimm[i]):
            resp = input("Already in sync. Retrain? [Y/n] ")
            if resp.lower() == "y":
                fire.retrain(_ddimm[i], verbose=1)
            continue
    
        setup_ddimm_path(_ddimm[i], _busnum)
        #checkpath(_busnum)
        try:
            explorer = Explorer(fire.freq, _busnum)
            print("\n----------        Explorer OMI Training Sequence ------------")
            explorer.sync()
            sleep(1)
            print("\n----------        Fire     OMI Training Sequence ------------")
            fire.sync(_ddimm[i])
            print("DDIMM{} sync Reg: ".format(_ddimm[i].upper()), end="")
            sleep(1)
            explorer.check_sync()
        except Exception as e:
            print(traceback.format_exc())
            print("Error. Please make sure you ran init command first (After a reset and initpath).")
    
main.add_command(sync)


#########################################################
#                  DDIMM CONFIGURATION                  #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to sync. Write the letters of DDIMMs without spaces.
                (Examples: a, b, ab)''')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def ddimmcfg(_busnum, _ddimm, _freq):
    " Configures the provided DDIMM with Fire. "
    fire = Fire(_busnum, _freq)

    for i in range (0, len(_ddimm)):
        if _ddimm[i] == "a":
            ddimm_add_adj=0x00000000
        elif _ddimm[i] == "b":
            ddimm_add_adj=0x00000400
        else: print("ERROR: incorrect ddimm selection !!")

        explorer = Explorer(fire.freq, _busnum)
        eeprom   = Eeprom(_busnum)

        print("   ------------    \nConfiguring DDIMM{}...".format(_ddimm[i].upper()), end=" \n")
        setup_ddimm_path(_ddimm[i], _busnum)
        print("DDIMM{} Configuration ".format(_ddimm[i].upper()), end="\n")
        """getting Memory size """
        eeprom = Eeprom(_busnum)
        _memory_size = eeprom.get_info()
        """ getting Vendor ID in Fire's reg : 0x2001040X00000000 with 
        0x10000006361014 for IBM/MICRON
        0xff010002ff010002 for SMART
        doesn't work properly
        Using alternative method"""
                
        """vendor_reg = explorer.i2c_double_read(0x20b080)
        logging.info(hex(vendor_reg))
        if (vendor_reg == 0x00000000000796): _vendor = "SMART"
        elif (vendor_reg == 0x00000000000596) or (vendor_reg == 0x00000000000197):_vendor = "IBM/MICRON"
        else:print("ERROR: Bad Vendor ID :")
        print("Vendor      :", end=" ")
        print(_vendor)
        logging.info(hex(ddimm_add_adj))"""

        data = eeprom.get_info()
        _memory_size = data[0]
        _vendor = data[1]


        fire.reg_ops(fire.steps2122, _ddimm[i], _vendor, _memory_size)
        fire.reg_ops(fire.steps25_a0, _ddimm[i], _vendor, _memory_size)

        if _vendor == "MICRON":
            fire.reg_ops(fire.steps25_a1_MICRON, _ddimm[i], _vendor, _memory_size)
        elif _vendor == "SMART":
            fire.reg_ops(fire.steps25_a1_SMART, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID"); return 1
    
        fire.reg_ops(fire.steps25_a2, _ddimm[i], _vendor, _memory_size)

        if _memory_size == 32:
            fire.reg_ops(fire.steps25_a3_32, _ddimm[i], _vendor, _memory_size)
        elif _memory_size == 64:
            fire.reg_ops(fire.steps25_a3_64, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Bad Memory size"); return 1

        fire.reg_ops(fire.steps25_a4, _ddimm[i], _vendor, _memory_size)

        if _memory_size == 32:
            fire.reg_ops(fire.steps25_a5_32, _ddimm[i], _vendor, _memory_size)
        elif _memory_size == 64:
            fire.reg_ops(fire.steps25_a5_64, _ddimm[i], _vendor, _memory_size)
    
        fire.reg_ops(fire.steps25_a6, _ddimm[i], _vendor, _memory_size)

        if _memory_size == 32:
            fire.reg_ops(fire.steps25_a7_32, _ddimm[i], _vendor, _memory_size)
        elif _memory_size == 64:
            fire.reg_ops(fire.steps25_a7_64, _ddimm[i], _vendor, _memory_size)

        fire.reg_ops(fire.steps25_a8, _ddimm[i], _vendor, _memory_size)

        if _vendor == "MICRON":
            fire.reg_ops(fire.steps25_a9_MICRON, _ddimm[i], _vendor, _memory_size)
        elif _vendor == "SMART":
            fire.reg_ops(fire.steps25_a9_SMART, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID"); return 1
    
        fire.reg_ops(fire.steps25_a10, _ddimm[i], _vendor, _memory_size)   

        if (_vendor == "MICRON") & (_memory_size == 32):
            fire.reg_ops(fire.steps25_a11_MICRON_32, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "MICRON") & (_memory_size == 64):
            fire.reg_ops(fire.steps25_a11_MICRON_64, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "SMART") & (_memory_size == 32):
            fire.reg_ops(fire.steps25_a11_SMART_32, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "SMART") & (_memory_size == 64):
            fire.reg_ops(fire.steps25_a11_SMART_64, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID/Memory size combination"); return 1

        check_status(_busnum, _ddimm[i], _freq)

        fire.reg_ops(fire.steps25_b, _ddimm[i], _vendor, _memory_size)

        if _memory_size == 32:
            fire.reg_ops(fire.step26_a0_32, _ddimm[i], _vendor, _memory_size)
        elif _memory_size == 64:
            fire.reg_ops(fire.step26_a0_64, _ddimm[i], _vendor, _memory_size)

        fire.reg_ops(fire.step26_a1, _ddimm[i], _vendor, _memory_size)

        if _vendor == "MICRON":
            fire.reg_ops(fire.step26_a2_MICRON, _ddimm[i], _vendor, _memory_size)
        elif _vendor == "SMART":
            fire.reg_ops(fire.step26_a2_SMART, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID"); return 1

        fire.reg_ops(fire.steps26_a3, _ddimm[i], _vendor, _memory_size)

        if (_vendor == "MICRON") & (_memory_size == 32):
            fire.reg_ops(fire.steps26_a4_MICRON_32, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "MICRON") & (_memory_size == 64):
            fire.reg_ops(fire.steps26_a4_MICRON_64, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "SMART") & (_memory_size == 32):
            fire.reg_ops(fire.steps26_a4_SMART_32, _ddimm[i], _vendor, _memory_size)
        elif (_vendor == "SMART") & (_memory_size == 64):
            fire.reg_ops(fire.steps26_a4_SMART_64, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID/Memory size combination"); return 1

        check_status(_busnum, _ddimm[i], _freq)

        fire.reg_ops(fire.steps_26b0, _ddimm[i], _vendor, _memory_size)

        if _vendor == "MICRON":
            fire.reg_ops(fire.steps_26b1_MICRON, _ddimm[i], _vendor, _memory_size)
        elif _vendor == "SMART":
            fire.reg_ops(fire.steps_26b1_SMART, _ddimm[i], _vendor, _memory_size)
        else: print("ERROR: Unsupported Vendor ID"); return 1

        fire.reg_ops(fire.steps_26b2, _ddimm[i], _vendor, _memory_size)
        fire.reg_ops(fire.steps27_a0, _ddimm[i], _vendor, _memory_size)

        if _memory_size == 32:
            fire.reg_ops(fire.steps27_a1_32, _ddimm[i], _vendor, _memory_size)
        elif _memory_size == 64:
            fire.reg_ops(fire.steps27_a1_64, _ddimm[i], _vendor, _memory_size)

        fire.reg_ops(fire.steps27_a2, _ddimm[i], _vendor, _memory_size)


        try:
            explorer = Explorer(fire.freq, _busnum)

        except Exception as e:
            print(traceback.format_exc())
            print("Error. Please make sure you ran init command first (After a reset and initpath).")

main.add_command(ddimmcfg)

#########################################################
#                  CHECKER                              #
#########################################################

def check_status(_busnum, _ddimm, _freq):
    fire = Fire(_busnum, _freq)
    explorer = Explorer(fire.freq, _busnum)    
    logging.info(_ddimm)
    if _ddimm == "a":
        ddimm_add_adj=0x00000000
    elif _ddimm == "b":
        ddimm_add_adj=0x00000400
    else: print("ERROR: incorrect ddimm selection !!")

    c = 0
    while (hex(fire.i2cread(0x2001000100002058+(ddimm_add_adj<<32))) != "0x1"):
        logging.info("waiting for response RDY")
        sleep(1)
        c=c+1
        if (c == 50):
            return 1
    logging.info("0x2058 is : " + hex(fire.i2cread(0x2001000100002058+(ddimm_add_adj<<32))))
    if fire.i2cread(0x300100010103FF20+(ddimm_add_adj<<32)) != 1: logging.info("Failure 0x30010x010103FF20 is not 0x1 !!"); return 1

#########################################################
#                  FBIST CONFIGURATION                  #
#           eg python3 omi.py --log fbistcfg -d a """   #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to sync. Write the letters of DDIMMs without spaces.
                (Examples: a, b, ab)''')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def fbistcfg(_busnum, _ddimm, _freq):
    " Runs a fbist test on selected DDIMM. "
    fire = Fire(_busnum, _freq)
    fbist = Fbist()

    fbist.fbist(_busnum, _ddimm)
    #fbist.fbist_stats_wr(_busnum, _ddimm)
    
main.add_command(fbistcfg)

#########################################################
#                  Firware Update                       #
#           eg python3 omi.py firmudpt -d a       #
#########################################################
# Firmware was reverse engineered from Cronus loading routine
# the reg dump was processed in excel to extract the list of writes / checking sequences.
# last reads were suppressed as they generate an I2C erros.
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to sync (only a is supported)''')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def firmupd(_busnum, _ddimm, _freq):
    " Loads firmware on DDIMM A only. "

    if _ddimm == "a":
        ddimm_add_adj=0x00000000
    elif _ddimm == "b":
        print("WARNING : Update has been tested only on DDIMM A !"); return 1;
        ddimm_add_adj=0x00000400  # not being used yet !
    else: print("ERROR: incorrect ddimm selection !!")

    firmware_file = "./CL444714.seq"
    print("\n----------------------------------\nFirmware update with",firmware_file,"code\n")
    f = open(firmware_file, "r")
    # counting lines of firmware
    with f:
        for count, line in enumerate(f):
            pass
    print('Total Lines', count + 1,'\nUpdate will take several minutes with software I2C ...')
    print('Both comments and progression data might freeze !')
    nblines = count +1
    print(nblines)
    f.close()
    if nblines != 243622:
        print("ERROR: Firmware file is corrupted: Bad number of firmware lines")
        return 1

    fire = Fire(_busnum, _freq)
    explorer = Explorer(fire.freq, _busnum)     
    print("----------------------------------\nCurrent Firmware information:\n")
    explorer.getinfo()
    explorer.get_firmware_info()
    
    l = 1 # number of lines
    r = 0 # number of reads
    
    with open(firmware_file) as f:
        for line in f:
            l=l+1
            #if (l % 500) == 0: print("\r",l, end='')
            line = line.split()      # will provide the elements of a line
            RW = line[0]             # catches the 1st element as R or W
            data = line[2]           # catches data after comma
            data_int=int(data, 0)    # converts hexa str into an int with autobase(0) 
            #print("{:#018x}".format(data_int))
            #logging.info("data_int {:#018x}".format(data_int))
            if 'W' in RW:
                #logging.info("WRITING EXPLORER REG: " + "0x{:0>16x}".format(data_int) )
                explorer.i2c_simple_write(data_int);
                #print("response is ,{:#018x}".format(explorer.i2c_simple_read(0x2)))
            elif 'R' in RW:
                if 'A0002058' in data:
                    r=r+1
                    p=r/2973*100    # we use the number of reads to avoid counting for each line
                    rprt = round(p, 1)
                    if (rprt % 2) == 0:
                        print("\rLine :", l, "/",nblines, "(",rprt, "%)", end='', flush=True)
                    # initial read steps for 0x404A0002058
                    explorer.i2c_simple_write(0x0304A0002058);
                    #explorer.i2c_simple_read(0x2);
                    explorer.i2c_simple_write(0x0404A0002058);
                    fc = 0  # number of failing tests
                    while (hex(explorer.i2c_simple_read(0x2)) != "0x1"):
                        #logging.info("waiting for response RDY")
                        #print("waiting for response RDY")
                        #preparing next read steps for 0x404A0002058
                        explorer.i2c_simple_write(0x0304A0002058);
                        #explorer.i2c_simple_read(0x2);
                        explorer.i2c_simple_write(0x0404A0002058);
                        sleep(0.01);  # allow 10ms to obtain firmware readyness
                        fc=fc+1;
                        #logging.info(fc);
                        if (fc == 10):
                            print("10 failing tests on 0x4040A0002058 test for 0x1");print("line is:",l);return 1
                    #debug read check for user
                    #explorer.i2c_simple_write(0x0304A00002058);
                    #explorer.i2c_simple_read(0x2);
                    #explorer.i2c_simple_write(0x0404A0002058);
                    #logging.info("0x0404A0002058 read response is ,{:#018x}".format(explorer.i2c_simple_read(0x2)));

                elif 'A103FF20' in data:
                    #print("Checking FF20")
                    explorer.i2c_simple_write(0x0304A103FF20);
                    #explorer.i2c_simple_read(0x2);
                    explorer.i2c_simple_write(0x0404A103FF20);
                    byte0_of_ff20 = explorer.i2c_simple_read(0x2) & 0x00FF
                    #logging.info("byte0_of_ff20 is:",hex(byte0_of_ff20))
                    if byte0_of_ff20 == 0x00:
                        pass
                        #logging.info("byte 0 of 0x0404A103FF20 is 00")
                    else: print("ERROR : byte 0 of 0x0404A103FF20 is not 00");print("Error occured at line is:",l); return 1
    
    # all I2C operations seem locked for a while at this level.
    print("\nEnd of firmware update.\nI2C operations are not possible during the firmware update for a while.\nYou might need to restart the DDIMM several times\nFurther check update with: python3 omy.py info -c explorer")
                                        

main.add_command(firmupd)

if __name__ == "__main__":
    main()


