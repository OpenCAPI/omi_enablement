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

# Test code to load a new firmware in a DDIMM with Explorer chip (OMI standard)
# Date    : 2022 oct 12
# Assumes Fire is set at 333MHz and I2C bus is 3

import resource
import os
from time import sleep
import binascii
import array
import struct
from crc32 import crc32_array
from fire import *
from explorer import *
from datetime import datetime

# Declarations 
revision     = "0.0"
padding      = 0
W64          = 0 # number of 32bytes word read from bin file
addr_index   = 0 # index used to calculate the write address XX in 0x0508A102FFXX
ID           = 0x4244  # to be incremented in the command buffer
data_buff_nb = 0x0
data_index   = 0
data_buff    = []     # reserving 64 32bits data for crc calculation 
for i in range(64):
    data_buff.append(0)

commit       = 0   # command buffer will be of commit type at the end of the firmware upload, otherwise regular command buffer are sent
cmd_buff     = []  # reserving 16 32bits data for crc calculation 
for i in range(16):
    cmd_buff.append("")

# get the latest firmware at : https://github.com/open-power/ocmb-explorer-fw/releases"
# after unzip, rename signed_app_fw.mem into <release>.bin
# Rename the follwing variable with the relaese name eg : 
#firmware_file = "CL444714.bin"
firmware_file = "<release>.bin"
#Uncomment the following lines if you don't want to log (see next print_to_log() function)
log_file = "./firmware_update.log"
#comparison_log_file="./excel_compa.log"

def print_to_log(data_to_print):       # to log sequence of 
    try:
        log_file
        log.write(data_to_print)
        log.write("\n")
    except:
        pass # print(data_to_print)

# the following will split the 64b word in 2 and fill the data_buff accordingly
def split_word_fill_data_buff(word):
    global data_buff
    global Ldata
    global Hdata
    data = struct.unpack('<Q', word)   # extract in little endian mode (<)
    Ldata = data[0] & 0xFFFFFFFF
    Hdata = data[0]>>32
    Ldata_txt = ("{:08x} ".format(Ldata))
    Hdata_txt = ("{:08x} ".format(Hdata))
    #Contribution to the crc32
    data_buff[data_index]   = "0x"+Ldata_txt  # storing the data 2 by 2 for data buffer crc32 calc
    data_buff[data_index+1] = "0x"+Hdata_txt
    #print("Ldata is: {:08X}".format(Ldata))   # {:#08X} => 0xbff72a5e | {:08X} => bff72a5e
    #print("Hdata is: {:08X}".format(Hdata))

def send_data_to_explorer():
    global data_buff
    global data_index
    global addr_index
    global Ldata
    global Hdata

    try:
        compa_log
        # to compare with excel cleaned cronus log
        write_str = "        'W' , 0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Ldata)+" ,")
        compa_log.write(write_str)
        compa_log.write("\n")
    except: pass

    # writing 2 data burst
    print_to_log("W 0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Ldata)))
    write_data = "0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Ldata))
    write_data_int=int(write_data, 0)    # converts hexa str into an int with autobase(0) 
    explorer.i2c_simple_write(write_data_int)
    #print(explorer.i2c_simple_read(write_data_int))

    addr_index = addr_index + 4  # preparing next addr_index

    try:
        compa_log
        # to compare with excel cleaned cronus log
        write_str = "        'W' , 0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Hdata)+" ,")
        compa_log.write(write_str)
        compa_log.write("\n")    
    except: pass

    print_to_log("W 0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Hdata)))
    write_data = "0x0508A102FF" + "{:02X}".format(addr_index) + ("{:08X}".format(Hdata))
    write_data_int=int(write_data, 0)    # converts hexa str into an int with autobase(0)
    explorer.i2c_simple_write(write_data_int)

    addr_index = addr_index + 4  # preparing next addr addr_index

# preparing command buffer template
cmd_buff_list = (
    "WXYT0108",
    "00000100",
    "CRC_DATA",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "0AED2801",
    "00000NBR",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "_CRC_CMD",
        )

# preparing last command (commit) buffer template
commit_buff_list = (
    "WXYT0008",
    "00000000",
    "FFFFFFFF",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000002",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "00000000",
    "_CRC_CMD",
        )

def send_command_burst(commit):
    global cmd_buff
    global ID
    global addr_index

    if commit == 0:
        for i in range(0, len(cmd_buff_list), 1):
            cmd_buff[i] =  cmd_buff_list[i]
        cmd_buff[0] = "{:04X}".format(ID) + "0108"
        cmd_buff[2] = "{:08X}".format(crc32_data)
        cmd_buff[9] = "00000" + "{:03X}".format(data_buff_nb)

    else:
        for i in range(0, len(commit_buff_list), 1):
            cmd_buff[i] =  commit_buff_list[i]
        cmd_buff[0] = "{:04X}".format(ID) + "0008"  # see page 105 of FW doc

    for cmd in cmd_buff:
        cmd="0x"+cmd                   # to provide hexa str to crc32 routine
        #print(cmd)

    crc32_cmd = crc32_array(cmd_buff, 15)
    cmd_buff[15] = "{:08X}".format(crc32_cmd)  # suppressing the 0x

    for cmd in cmd_buff:
        try:
            compa_log
            # to compare with excel cleaned cronus log
            cmd_str = ("        'W' , 0x0508A103FF" + "{:02X}".format(addr_index) + cmd  + " ,")
            compa_log.write(cmd_str)
            compa_log.write("\n")
        except: pass

        print_to_log("W 0x0508A103FF" + "{:02X}".format(addr_index) + cmd)
        cmd = "0x0508A103FF" + "{:02X}".format(addr_index) + cmd
        cmd_int=int(cmd, 0)    # converts hexa str into an int with autobase(0)
        explorer.i2c_simple_write(cmd_int)

        addr_index = addr_index + 4

def clr_inbound_doorbell():
    try:
        compa_log
        # to compare with excel cleaned cronus log
        db_str = "        'W' , 0x0508A808473880000000 ,\n        'W' , 0x0508A808473C00000000 ,"
        compa_log.write(db_str)
        compa_log.write("\n")               
    except: pass

    print_to_log("W 0x0508A808473880000000")
    explorer.i2c_simple_write(0x0508A808473880000000)
    print_to_log("W 0x0508A808473C00000000")
    explorer.i2c_simple_write(0x0508A808473C00000000)


def clr_outbound_doorbell():
    try:
        compa_log
        # to compare with excel cleaned cronus log
        db_str = "        'W' , 0x0508A000205800000001 ,"
        compa_log.write(db_str)
        compa_log.write("\n")               
    except: pass

    print_to_log("W 0x0508A000205800000001")
    explorer.i2c_simple_write(0x0508A000205800000001)

def set_inbound_doorbell():
    try:
        compa_log
        # to compare with excel cleaned cronus log
        str = "        'W' , 0x0508A808473080000000 ,\n        'W' , 0x0508A808473400000000 ,"
        compa_log.write(str)
        compa_log.write("\n")
    except: pass

    print_to_log("W 0x0508A808473080000000")
    explorer.i2c_simple_write(0x0508A808473080000000)
    print_to_log("W 0x0508A808473400000000")
    explorer.i2c_simple_write(0x0508A808473400000000)    

def waiting_fw_rdy():
    explorer.i2c_simple_write(0x0304A0002058);  
    #explorer.i2c_simple_read(0x2);
    explorer.i2c_simple_write(0x0404A0002058);

    try:
        compa_log
        # to compare with excel cleaned cronus log
        str = "        'R' , 0x0404A0002058 ,"
        compa_log.write(str)
        compa_log.write("\n")
    except: pass

    print_to_log("R 0x0404A0002058")

    fc = 0  # number of failing tests (Failing counter)
    reg02 = hex(explorer.i2c_simple_read(0x2))
    print_to_log(reg02)
    
    
    while (reg02 != "0x1"):
        print_to_log("waiting for response RDY")   ###
        #preparing next read steps for 0x404A0002058
        explorer.i2c_simple_write(0x0304A0002058);
        print_to_log("W 0x0404A0002058")           ####
        explorer.i2c_simple_write(0x0404A0002058);
        sleep(0.05);  # allow 10 msec to obtain firmware readyness
        fc=fc+1;
        #logging.info(fc);
        
        if (fc == 5):
            print("4 failing tests on 0x4040A0002058 test for 0x1");exit()
        
        reg02 = hex(explorer.i2c_simple_read(0x2))
        print_to_log(reg02)

def sanity_check(last):
    explorer.i2c_simple_write(0x0304A103FF20);
    #print_to_log("0x0304A103FF20")
    #explorer.i2c_simple_read(0x2);
    explorer.i2c_simple_write(0x0404A103FF20);
    print_to_log("R 0x0404A103FF20")
    ff20_content = explorer.i2c_simple_read(0x2)

    try:
        compa_log
        # to compare with excel cleaned cronus log
        str = "        'R' , 0x0404A103FF20 ,"
        compa_log.write(str)
        compa_log.write("\n")
    except: pass

    print_to_log(hex(ff20_content))
    if last==1:
        if ff20_content == 0x4c00:
            print("firmware upload is successful")
        else:
            byte0_of_ff20 = ff20_content & 0x00FF
            #byte0_of_ff20 = 0
            #logging.info("byte0_of_ff20 is:",hex(byte0_of_ff20))
            if byte0_of_ff20 == 0x00:
                pass
                #logging.info("byte 0 of 0x0404A103FF20 is 00")
            else: 
                print("ERROR : byte 0 of 0x0404A103FF20 is not 00")
                print_to_log("ERROR : byte 0 of register 0xA103FF20 is not 00")
                exit()

# --------------------------#
# main program starts here
# --------------------------#

# to use fire and explorer routines
fire = Fire(3, 333)
explorer = Explorer(fire.freq, 3)

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)	

if firmware_file == "<release>.bin":
    print("Check https://github.com/open-power/ocmb-explorer-fw/releases")
    print("to get latest DDIMM EXPLORER firmware")
    print("and update variable firmware_file = \"<release>.bin\" accordingly")
    exit(1)

try:
    log_file
    log      = open(log_file, "w")           # Makes sure the file is clean at startup
    log.close
    log      = open(log_file, "a")           # will append the prints
    log.write("OMI DDIMM Firmware update log\n" + dt_string + "\nFile used: " + firmware_file)        # time stamp
except: pass

try:
    comparison_log_file
    compa_log      = open(comparison_log_file, "w")           # Makes sure the file is clean at startup
    compa_log.close
    compa_log      = open(comparison_log_file, "a")           # will append the prints
except: pass

print("Firmware reading from:",firmware_file, " binary file")

file_size = os.path.getsize(firmware_file)
print("File Size is :", file_size, "bytes")
rest = 256 - (file_size % 256)    # provides information if padding will be required at the end of the file
burst_nb = file_size // 256

print("Bursts to be written :", burst_nb, " Will remain " + "{:d} ".format(rest) + "bytes to pad in the last data buffer")

f = open(firmware_file, "rb")

word = f.read(8)  # ready to begin collecting first data from binfile
while word:       # word is either a 64b word from the bin file, or a 0xFFFFFFFFFFFFFFFF padding at the end of the file if required
    W64=W64+1     # counting 64B word from 1 at first loop

    split_word_fill_data_buff(word) # we split the 64b word in 2 32b words
    data_index = data_index + 2     # we stored 2 32bits words in the data buff
    send_data_to_explorer()         # addr_index will be incremented by 4 + 4

    # once we have read 256 bytes (32 W64), we need to prepare the corresponding command buffer
    #------------------------------------------------------------------------------------------#
    if addr_index > 0xfc:

        addr_index = 0x40                 # prepares next cmd set. First address will be 0xA103FF40
        data_index = 0                    # prepares next crc calculation
        crc32_data = crc32_array(data_buff, 64)  # compute the data_buff crc32

        clr_inbound_doorbell()             #Clear inbound doorbell => WR 1 in bit 31 of @A8084738 - all others at 0        
        clr_outbound_doorbell()            #Clear outbound doorbell... => WR 1 in bit 0 of @A0002058

        send_command_burst(0)             # sending regular command burst (not the last commit one)

        addr_index = 0x00                 # prepares next cmd set first address will be 0x0508A103FF40
        data_buff_nb = data_buff_nb + 1   # prepares next data buffer number
        #print(data_buff_nb)
        ID = ID+1                         # prepares next data buffer ID number
        #print("ID={:04X}".format(ID))

        for i in range(64):               # cleaning data buffer for next crc32
            data_buff.append(0)

        #last commands of the burst
        #-------------------------#
        
        set_inbound_doorbell()      #Set the inbound doorbell => WR 1 in bit 31 of @A8084730 - all others at 0
        waiting_fw_rdy()    #Poll for response ready => Read Outbound doorbell @A002058 => Poll until 0400000001

        # Every 16 bursts, we check perform a sanity check and also for the first one
        if ((data_buff_nb-1) % 16)==0:
            sanity_check(0)
            progress = round(data_buff_nb / burst_nb * 100, 1)
            print("\rProgress: ",progress, "%", end='', flush=True)   # we compute progress once in a while.

        clr_outbound_doorbell()


    
    word = f.read(8)               # prepares next loop if any (otherwise check if padding is required)
    if (not word) & (rest !=0):    # Situation of padding occurs
        word = b'\xff\xff\xff\xff\xff\xff\xff\xff'
        padding = padding + 8      # We increase by 8 bytes the counting as we work with 64B words
        if (padding > rest):       # need to stop padding at some time 
            break

# last step : commit the code => last commands buffer to be issued
#----------------------------------------------------------------#

clr_inbound_doorbell()
clr_outbound_doorbell()

addr_index = 0x40                 # prepares last cmd set. First address will be 0xA103FF40

send_command_burst(1)             # sending a "commit" type command burst (not the regular ones)

#last commands after the commit burst
set_inbound_doorbell()

print("\rProgress: 100 %       ", end='', flush=True)
print("\nWaiting 30s to allow firmware to handle the binary data ...")
sleep(30)
waiting_fw_rdy()    #Poll for response ready => Read Outbound doorbell @A002058 => Poll until 0400000001
# DEBUG
sanity_check(1)     # Last check we check value is 0xC00
#clr_outbound_doorbell()


for i in range(15):                         # cleaning cmd_buff buffer for next crc32
    cmd_buff.append(0)

#print("\nnumber of W64:   ", W64)
#print("\nnumber of bursts:", data_buff_nb)

#firmwarefile close
f.close
#log file close if any
try:
    log_file
    log.close
    #compa_log file close if any
except: pass

try:
    compa_log
    compa_log.close
except: pass
    
'''print("\n----------------------------------\nCurrent Firmware information:\n")
explorer.getinfo()
explorer.get_firmware_info()'''

print("\nEnd of firmware upload step\nYou might need to restart the DDIMM several times while allowing some time for firmware to update between reset\nCheck update with: python3 omy.py info -c explorer")


print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)
