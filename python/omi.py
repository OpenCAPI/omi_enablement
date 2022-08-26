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

import click
import traceback
from time import sleep

from fire import *
from explorer import *
from ice import *
from components import *
from constants import *
from functions import *

import traceback

@click.group()
@click.option('--log/--no-log', default=False, help='Display more info about the execution of the command.')
def main(log):
    if log : logging.basicConfig(level=logging.INFO)

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
    " Initialize the explorer chip. This must be done before any other operation. "
    fire = Fire(_busnum, _freq)
    explorer = Explorer(fire.freq, _busnum)
    explorer.init()
main.add_command(init)


@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def info(_chip, _busnum, _freq):
    " Get chip internal information. "
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        print("ID:", hex(fire.id))
        print("Dirty bit:", fire.is_dirty)
        print("Frequency:", fire.freq, "MHz")
    elif _chip.lower() in ["explorer", "exp", "ice"]:
        explorer = Explorer(fire.freq, _busnum)
        eeprom = Eeprom()
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


@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def read(_register, _chip, _busnum, _freq):
    "Read from an internal register of a program."
    _register = int(_register, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        print(hex(fire.i2cread(_register)))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        print(hex(explorer.i2c_double_read(_register)))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
main.add_command(read)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or EXPLORER/ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def i2cread(_register, _chip, _busnum, _freq):
    "Read from an internal register of a program."
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
            print(explorer.i2cread(0x2))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2cread(_register)))
main.add_command(i2cread)


@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-r', '--register', '_register', type=str, required=True, nargs=1, help='Register address to read (in hex)')
@click.option('-d', '--data', '_data', type=str, required=True, nargs=1, help='Data value to write to the register (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def write(_register, _data, _chip, _busnum, _freq):
    "Write to an internal register of a program."
    _register = int(_register, 16)
    _data = int(_data, 16)
    fire = Fire(_busnum, _freq)
    if _chip.lower() == "fire":
        res = fire.i2cwrite(_register, _data)
        print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["explorer", "exp"]:
        explorer = Explorer(fire.freq, _busnum)
        res = explorer.i2c_double_write(_register, _data)
        print("Writing check : {}".format("Success" if res else "Failed"))
    elif _chip.lower() in ["ice", "gemini"]:
        ice = Ice(fire.freq, _busnum)
        print(hex(ice.i2c_double_read(_register)))
    else:
        print("Chip provided is incorrect.")
    
main.add_command(write)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--data', '_data', type=str, required=True, nargs=1, help='Data value to write to the register (in hex)')
@click.option('-c', '--chip', '_chip', type=str, required=True, nargs=1, help='Chip to read from (FIRE or ICE)')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def i2cwrite(_data, _chip, _busnum, _freq):
    "Write to an internal register of a program."
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

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to reset. Write the letters of DDIMMs to reset without spaces.
                (Examples: abcdsw, bdw, s)''')
@click.option('-s', '--state', '_state', type=str, required=True, nargs=1, help='on: RESET ON | off: RESET OFF')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def ddimmreset(_ddimm, _state, _busnum, _freq):
    "Set the reset state of the DDIMMs (In RESET mode : ON | Out RESET mode : OFF)."
    fire = Fire(_busnum, _freq)
    if _state.lower() == "on": fire.set_ddimm_on_reset(_ddimm)
    elif _state.lower() == "off": fire.set_ddimm_off_reset(_ddimm)
    else : print("State provided is not supported.")

main.add_command(ddimmreset)

#########################################################
#                                                       #
#                   DDIMMs Path                         #
#                                                       #
#########################################################

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMM (only one or none) to setup their path.
                (Examples: a, b none)''')
def initpath(_busnum, _ddimm):
    " Setup path to access a provided DDIMM. "
    if len(_ddimm) > 1 and _ddimm.lower() != "none":
        print("Please provide a valid ddimm letter (a or b) or none.")
        return
    setup_ddimm_path(_ddimm, _busnum)
main.add_command(initpath)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
def checkpath(_busnum):
    " Gets the current path configuration. "
    path_status()
main.add_command(checkpath)



#########################################################
#                                                       #
#                       SYNCING                         #
#                                                       #
#########################################################
@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to check their sync. Write the letters of DDIMMs to reset without spaces.
                (Examples: a, b, ab)''')

@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def checksync(_busnum, _ddimm, _freq):
    " Check for the training/syncing status of a DDIMM. "
    fire = Fire(_busnum, _freq)
    fire.check_sync(_ddimm, verbose=1)

main.add_command(checksync)

@click.command()
@click.option('-b', '--busnum', '_busnum', type=int, default=3, nargs=1, help='I2C bus number (default=3)')
@click.option('-d', '--ddimm', '_ddimm', type=str, required=True, nargs=1, help='''DDIMMs to sync. Write the letters of DDIMMs without spaces.
                (Examples: a, b, ab)''')
@click.option('-f', '--freq', '_freq', type=int, default=333, nargs=1, help='Fire\'s frequency. The program will try to retrieve automatically the version. This value will be used otherwise. (default=333)')
def sync(_busnum, _ddimm, _freq):
    " Train/Sync the provided DDIMM with Fire. "
    fire = Fire(_busnum, _freq)
    
    for i in range (0, len(_ddimm)):
        print("Sync DDIMM{}...".format(_ddimm[i].upper()), end=" ")
        if fire.check_sync(_ddimm[i]):
            resp = input("Already in sync. Retrain? [Y/n] ")
            if resp.lower() == "y":
                fire.retrain(_ddimm[i], verbose=1)
            continue
    
        setup_ddimm_path(_ddimm[i], _busnum)
        try:
            explorer = Explorer(fire.freq, _busnum)
            explorer.sync()
            sleep(1)
            fire.sync(_ddimm[i])
            print("DDIMM{} sync: ".format(_ddimm[i].upper()), end="")
            sleep(1)
            explorer.check_sync()
        except Exception as e:
            print("Error. Please make sure you ran init command first (After a reset and initpath).")
    
main.add_command(sync)



if __name__ == "__main__":
    main()
