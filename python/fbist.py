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
from fire import *
from explorer import *

##################################################################################
#    This class contains the Fbist generator (configuration, test and analysis   #
##################################################################################

class Fbist:

	def fbist(self, _busnum, _ddimm):
		fire = Fire(_busnum)
		
		print("")
		print("======================================================")
		print("-------------------Start FBIST procedure -------------")
		print("======================================================")
		print("")
		
		print("#=============================")
		print(" Commands configuration")

		number_of_engines_word = input(">> Number of Engines to enable ? (Type 1 to 8): ")
		number_of_engines = int(number_of_engines_word)

		access_type_word = input(">> Number of Bytes to test access? (Type 2 for 64B and 4 for 128B): ")
		access_type_int = int(access_type_word)

		flit_spacing_word = input(">> Number of cycles between flits (from FF to 0, typical is 0): ")
		flit_spacing_int = int(flit_spacing_word, 16)
		flit_spacing = int(0x0000000000000000 + flit_spacing_int)

		#===============
		#WRITE PROCEDURE
		print(">>                                                       ")
		if (access_type_int == 4):
			print(">> FBIST_POOL_0_ENGINE_x - 0x01=128B WR + 0x01=@Incremental address")
			access_type = 0x0000000000000101
		else:
			print(">> FBIST_POOL_0_ENGINE_x - 0x02= 64B WR + 0x01=@Incremental address")
			access_type = 0x0000000000000102

		# Enabling 1 to 8 engines with the same data + Disabling the unused one
		for x in range (0, 8):
			access_type_addr = int(0x0102000000000000 + 4*x)
			if (x < (int)(number_of_engines)):
				fire.i2cwrite(access_type_addr, access_type)
			else:
				fire.i2cwrite(access_type_addr, 0x0000000000000000)

		# The more spacing the less traffic -> 0 is giving the maximumm throughput
		print(">> Spacing of ", flit_spacing_int, "cycles between Flits")
		print(">>                                                       ")
		fire.i2cwrite(0x0102000000000020, flit_spacing)

		self.reg_ops(self.steps_fbist_writes, _busnum, _ddimm)
		print(" -- 6 secs run - please wait --")
		sleep(6)
		self.reg_ops(self.steps_fbist_stop, _busnum, _ddimm)

		self.fbist_stats_wr(_busnum, _ddimm)

		#==============
		#READ PROCEDURE
		print(">>                                                       ")
		if (access_type_int == 4):
			print(">> FBIST_POOL_0_ENGINE_x - 0x04=128B RD + 0x01=@Incremental address")
			access_type = 0x0000000000000104
		else:
			print(">> FBIST_POOL_0_ENGINE_x - 0x05= 64B RD + 0x01=@Incremental address")
			access_type = 0x0000000000000105

		# Enabling 1 to 8 engines with the same data + Disabling the unused one
		for x in range (0, 8):
			access_type_addr = int(0x0102000000000000 + 4*x)
			if (x < (int)(number_of_engines)):
				fire.i2cwrite(access_type_addr, access_type)
			else:
				fire.i2cwrite(access_type_addr, 0x0000000000000000)

		# The more spacing the less traffic -> 0 is giving the maximumm throughput
		print(">> Spacing of ", flit_spacing_int, "cycles between Flits")
		print(">>                                                       ")
		fire.i2cwrite(0x0102000000000020, flit_spacing)

		self.reg_ops(self.steps_fbist_reads, _busnum, _ddimm)
		print(" -- 6 secs run - please wait --")
		sleep(6)
		self.reg_ops(self.steps_fbist_stop, _busnum, _ddimm)

		self.fbist_stats_rd(_busnum, _ddimm)		

	steps_fbist_writes = ("steps_fbist_writes",
		'W' ,0x010200000000002C,0x0000000000000000,"FBIST POOL 0 ENGINE 0 ADDRESS START LOW",
		'W' ,0x0102000000000030,0x0000000000000000,"FBIST POOL 0 ENGINE 0 ADDRESS START HIGH",
		'W' ,0x0102000000000034,0x0000000000000000,"FBIST POOL 0 ENGINE 1 ADDRESS START LOW",
		'W' ,0x0102000000000038,0x0000000000000001,"FBIST POOL 0 ENGINE 1 ADDRESS START HIGH",
		'W' ,0x010200000000003C,0x0000000000000000,"FBIST POOL 0 ENGINE 2 ADDRESS START LOW",
		'W' ,0x0102000000000040,0x0000000000000002,"FBIST POOL 0 ENGINE 2 ADDRESS START HIGH",
		'W' ,0x0102000000000044,0x0000000000000000,"FBIST POOL 0 ENGINE 3 ADDRESS START LOW",
		'W' ,0x0102000000000048,0x0000000000000003,"FBIST POOL 0 ENGINE 3 ADDRESS START HIGH",
		'W' ,0x010200000000004C,0x0000000000000000,"FBIST POOL 0 ENGINE 4 ADDRESS START LOW",
		'W' ,0x0102000000000050,0x0000000000000004,"FBIST POOL 0 ENGINE 4 ADDRESS START HIGH",
		'W' ,0x0102000000000054,0x0000000000000000,"FBIST POOL 0 ENGINE 5 ADDRESS START LOW",
		'W' ,0x0102000000000058,0x0000000000000005,"FBIST POOL 0 ENGINE 5 ADDRESS START HIGH",
		'W' ,0x010200000000005C,0x0000000000000000,"FBIST POOL 0 ENGINE 6 ADDRESS START LOW",
		'W' ,0x0102000000000060,0x0000000000000006,"FBIST POOL 0 ENGINE 6 ADDRESS START HIGH",
		'W' ,0x0102000000000064,0x0000000000000000,"FBIST POOL 0 ENGINE 7 ADDRESS START LOW",
		'W' ,0x0102000000000068,0x0000000000000007,"FBIST POOL 0 ENGINE 7 ADDRESS START HIGH",
		'W' ,0x0102000000000094,0x0000000000000000,"FBIST DATA Pattern => 0x0: Data equals address",
		'W' ,0x0102000000000024,0x0000000000000000,"Arbitration algorithm for Pool 0 commands => 0x0 = Round robin",
		'R' ,0x0102000000000028,0x0000000000000000,"- Read clear Pool 0 Status and reet before start",
		'W' ,0x0102000000000090,0x0000000000000000,"FBIST ERROR - 0x00090 =>  to reset before start",
		'W' ,0x0102000000000028,0x0000000080000001,"FBIST POOL 0 STATUS - start - will stop on error",
		'R' ,0x0102000000000028,0x0000000080000004,"FBIST POOL 0 STATUS - check in progress",
		)

	steps_fbist_reads = ("steps_bist_reads",
		'W' ,0x010200000000002C,0x0000000000000000,"FBIST POOL 0 ENGINE 0 ADDRESS START LOW",
		'W' ,0x0102000000000030,0x0000000000000000,"FBIST POOL 0 ENGINE 0 ADDRESS START HIGH",
		'W' ,0x0102000000000034,0x0000000000000000,"FBIST POOL 0 ENGINE 1 ADDRESS START LOW",
		'W' ,0x0102000000000038,0x0000000000000001,"FBIST POOL 0 ENGINE 1 ADDRESS START HIGH",
		'W' ,0x010200000000003C,0x0000000000000000,"FBIST POOL 0 ENGINE 2 ADDRESS START LOW",
		'W' ,0x0102000000000040,0x0000000000000002,"FBIST POOL 0 ENGINE 2 ADDRESS START HIGH",
		'W' ,0x0102000000000044,0x0000000000000000,"FBIST POOL 0 ENGINE 3 ADDRESS START LOW",
		'W' ,0x0102000000000048,0x0000000000000003,"FBIST POOL 0 ENGINE 3 ADDRESS START HIGH",
		'W' ,0x010200000000004C,0x0000000000000000,"FBIST POOL 0 ENGINE 4 ADDRESS START LOW",
		'W' ,0x0102000000000050,0x0000000000000004,"FBIST POOL 0 ENGINE 4 ADDRESS START HIGH",
		'W' ,0x0102000000000054,0x0000000000000000,"FBIST POOL 0 ENGINE 5 ADDRESS START LOW",
		'W' ,0x0102000000000058,0x0000000000000005,"FBIST POOL 0 ENGINE 5 ADDRESS START HIGH",
		'W' ,0x010200000000005C,0x0000000000000000,"FBIST POOL 0 ENGINE 6 ADDRESS START LOW",
		'W' ,0x0102000000000060,0x0000000000000006,"FBIST POOL 0 ENGINE 6 ADDRESS START HIGH",
		'W' ,0x0102000000000064,0x0000000000000000,"FBIST POOL 0 ENGINE 7 ADDRESS START LOW",
		'W' ,0x0102000000000068,0x0000000000000007,"FBIST POOL 0 ENGINE 7 ADDRESS START HIGH",
		'W' ,0x0102000000000094,0x0000000000000000,"FBIST DATA Pattern => 0x0: Data equals address",
		'W' ,0x0102000000000024,0x0000000000000000,"Arbitration algorithm for Pool 0 commands => 0x0 = Round robin",
		'R' ,0x0102000000000028,0x0000000000000000,"- Read clear Pool 0 Status and reet before start",
		'W' ,0x0102000000000090,0x0000000000000000,"FBIST ERROR - 0x00090 =>  to reset before start",
		'W' ,0x0102000000000028,0x0000000080000001,"FBIST POOL 0 STATUS - start - will stop on error",
		'R' ,0x0102000000000028,0x0000000080000004,"FBIST POOL 0 STATUS - check in progress",
		)


	steps_fbist_stop = ("steps_fbist_stop",
		'R' ,0x0102000000000028,0x0000000080000004,"FBIST POOL 0 STATUS - check in progress",
		'W' ,0x0102000000000028,0x0000000000000002,"FBIST POOL 0 STATUS - stop",
		'R' ,0x0102000000000028,0x0000000000000000,"FBIST POOL 0 STATUS - status - 0:ok - 8= done with error",
		'R' ,0x0102000000000090,0x0000000000000000,"FBIST ERROR - 0x00090 => check 0:ok - 3=comp error - 9 hang",
		'R' ,0x01020000000000C4,"",                "FBIST_ERROR_ARRAY_INFO - C4 ",
		'R' ,0x01020000000000B0,"",                "FBIST POOL 0 STATS TEST TIME (MSB) - B0",
		'R' ,0x010200000000008C,"",                "FBIST POOL 0 STATS TEST TIME (LSB) - 8C",
		'R' ,0x010200000000007C,"",                "FBIST POOL 0 STATS NUMBER OF READS -7C",
		'R' ,0x0102000000000080,"",                "FBIST POOL 0 STATS NUMBER OF WRITES  - 80",
		'R' ,0x01020000000000A8,"",                "FBIST POOL 0 STATS NUMBER OF READ WRITES EXTENDED - A8",
		'R' ,0x0102000000000084,"",                "FBIST POOL 0 STATS NUMBER OF BYTES READ - 84",
		'R' ,0x0102000000000088,"",                "FBIST POOL 0 STATS NUMBER OF BYTES WRITTEN - 88",
		'R' ,0x01020000000000AC,"",                "FBIST POOL 0 STATS NUMBER OF BYTES READ WRITTEN EXTENDED - AC",
	)


	def fbist_stats_wr(self, _busnum, _ddimm):
		fire = Fire(_busnum)

		print("-------------------------")
		errors_found  = fire.i2cread(0x0102000000000090)
		if (errors_found):
			print("Errors     :  YES - see below type of error")
			# Describing the error status
			fbist_error_array_data = fire.i2cread(0x01020000000000C0)
			print("Error status : 0x{:0>08x}".format(fbist_error_array_data), "described as follow:")
			error_snapshot        = (fbist_error_array_data & 0xFF000000) >> 24
			error_snapshot_engine = (fbist_error_array_data & 0x00F00000) >> 20
			error_snapshot_act_tag= (fbist_error_array_data & 0x000FF000) >> 12
			error_snapshot_exp_tag= (fbist_error_array_data & 0x00000FF0) >>  4
			error_snapshot_dp     = (fbist_error_array_data & 0x0000000C) >>  2
			error_snapshot_ow     = (fbist_error_array_data & 0x00000002) >>  1
			error_snapshot_dmisc  = (fbist_error_array_data & 0x00000001)

			if   (error_snapshot_dmisc == 1): print (">> Data compare error ")
			if   (error_snapshot == 1): print (">> Good Write response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 2): print (">> Bad Write response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 3): print (">> Good Read response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 4): print (">> Bad Read response on engine number ", error_snapshot_engine)

			#print (">> Actual capptag: ",hex(error_snapshot_act_tag), " - Expected capptag: ",hex(error_snapshot_exp_tag))
			print (">> Actual capptag: 0x{:0>02x}".format(error_snapshot_act_tag), \
			       " - Expected capptag: 0x{:0>02x}".format(error_snapshot_exp_tag))
			print (">> OpenCAPI dpart : ",error_snapshot_dp, " - OpenCAPI OW : ",error_snapshot_ow)
			print("-------------------------")
		else:
			print("Errors     :  no errors found ")

		run_high = fire.i2cread(0x01020000000000B0)
		#run_high =0x0000000000000000
		#print("RUN TIME H :",run_high)
		run_low = fire.i2cread(0x010200000000008C)
		#run_low = 0x00000000788F9D15
		#print("RUN TIME L :",run_low)

		run_time = (run_low + (run_high << 32)) / (fire.freq*1E6)
		print("Run Time   : {:.2f} sec".format(run_time))

		#Read latency for every engine
		lat_high = fire.i2cread(0x01020000000000B8)
		lat_low = fire.i2cread(0x01020000000000B4)
		latency_E0 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E0 : {:0>.2f} secs".format(latency_E0))

		lat_high = fire.i2cread(0x01020000000000CC)
		lat_low = fire.i2cread(0x01020000000000BC)
		latency_E1 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E1 : {:0>.2f} secs".format(latency_E1))

		lat_high = fire.i2cread(0x01020000000000D4)
		lat_low = fire.i2cread(0x01020000000000D0)
		latency_E2 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E2 : {:0>.2f} secs".format(latency_E2))

		lat_high = fire.i2cread(0x01020000000000DC)
		lat_low = fire.i2cread(0x01020000000000D8)
		latency_E3 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E3 : {:0>.2f} secs".format(latency_E3))

		lat_high = fire.i2cread(0x01020000000000E4)
		lat_low = fire.i2cread(0x01020000000000E0)
		latency_E4 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E4 : {:0>.2f} secs".format(latency_E4))

		lat_high = fire.i2cread(0x01020000000000EC)
		lat_low = fire.i2cread(0x01020000000000E8)
		latency_E5 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E5 : {:0>.2f} secs".format(latency_E5))

		lat_high = fire.i2cread(0x01020000000000F4)
		lat_low = fire.i2cread(0x01020000000000F0)
		latency_E6 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E6 : {:0>.2f} secs".format(latency_E6))

		lat_high = fire.i2cread(0x01020000000000FC)
		lat_low = fire.i2cread(0x01020000000000F8)
		latency_E7 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E7 : {:0>.2f} secs".format(latency_E7))

		latency = latency_E0 + latency_E1 + latency_E2 + latency_E3 + latency_E4 + latency_E5 + latency_E6 + latency_E7
		print("Sum of lat : {:0>.2f} secs".format(latency))

		nb_wr_high = fire.i2cread(0x01020000000000A8)
		#nb_wr_high =0x0000000000000000 
		#print("nb_wr H :",nb_wr_high)
		nb_wr_low  = fire.i2cread(0x0102000000000080)
		#nb_wr_low  =0x0000000015C3D72B
		#print("nb_wr L :",nb_wr_low)
		# MSB for writes are only 4 digits left
		nb_wr      = nb_wr_low + (((nb_wr_high & 0xFFFF0000)>>16) << 32)
		#print("Total writes  = 0x{:0>16x}<<32".format(nb_wr_high) + "+ 0x{:0>16x}".format(nb_wr_low) + "= 0x{:0>16x}".format(nb_wr))
		print("Total WR   :",nb_wr)		

		nb_32Bwr_high = fire.i2cread(0x01020000000000AC)
		#nb_32Bwr_high =0x0000000000000000
		#print("nb_32Bwr H :",nb_32Bwr_high)
 
		nb_32Bwr_low  = fire.i2cread(0x0102000000000088)
		#nb_32Bwr_low  =0x000000002B87AE56
		#print("nb_32Bwr L :",nb_32Bwr_low)

		# MSB for writes are only 4 digits left
		nb_32Bwr      = nb_32Bwr_low + (((nb_32Bwr_high & 0xFFFF0000)>>16) << 32)
		print("nb 32B wr  :",nb_32Bwr)

		if (nb_wr != 0 ):
			if (nb_32Bwr/nb_wr == 2.0):
				print("Access is  : WRITE 64 Bytes")
			elif (nb_32Bwr/nb_wr == 4.0):
				print("Access is  : WRITE 128 Bytes")
			else:
				print("Access is  : WRITE nb_32Bwr/nb_wr Bytes!!")

		print("freq       :",fire.freq, "MHz")
		if (nb_wr != 0 ):
			avg_wr_lat = latency / nb_wr *1000000000
			print("Avg Wr lat : {:0>.2f} ns".format(avg_wr_lat))
		else:
			print("Avg Wr lat : NA")


		Throughput = nb_32Bwr * 32 / run_time / 1000000000
		print("Throughput : {:0>.2f} GBps".format(Throughput))

		print("-------------------------")

	def fbist_stats_rd(self, _busnum, _ddimm):
		fire = Fire(_busnum)

		print("-------------------------")
		errors_found  = fire.i2cread(0x0102000000000090)
		if (errors_found):
			#print ("FBIST ERROR ARRAY DATA - good responses? => RD @0x000C0 => expected : 0x0100_0000")
			#print (" 0x01xx_xxxx = good write - 0x02xx_xxxx = bad write")
			#print (" 0x03xx_xxxx = good read  - 0x04xx_xxxx = bad read response")
			#print (" READ 17x more times FBIST ERROR ARRAY DATA")

			print("Errors     :  YES - see below the 16 x 4 Bytes of the received data")
			print("0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)))
			print("0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)))
			print("0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)))
			print("0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)), \
			      "0x{:0>08x}".format(fire.i2cread(0x01020000000000C0)))

			# Describing the error status
			fbist_error_array_data = fire.i2cread(0x01020000000000C0)
			print("Error status : 0x{:0>08x}".format(fbist_error_array_data), "described as follow:")
			error_snapshot        = (fbist_error_array_data & 0xFF000000) >> 24
			error_snapshot_engine = (fbist_error_array_data & 0x00F00000) >> 20
			error_snapshot_act_tag= (fbist_error_array_data & 0x000FF000) >> 12
			error_snapshot_exp_tag= (fbist_error_array_data & 0x00000FF0) >>  4
			error_snapshot_dp     = (fbist_error_array_data & 0x0000000C) >>  2
			error_snapshot_ow     = (fbist_error_array_data & 0x00000002) >>  1
			error_snapshot_dmisc  = (fbist_error_array_data & 0x00000001)

			if   (error_snapshot_dmisc == 1): print (">> Data compare error ")
			if   (error_snapshot == 1): print (">> Good Write response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 2): print (">> Bad Write response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 3): print (">> Good Read response on engine number ", error_snapshot_engine)
			elif (error_snapshot == 4): print (">> Bad Read response on engine number ", error_snapshot_engine)

			print (">> Actual capptag: 0x{:0>02x}".format(error_snapshot_act_tag), \
			       " - Expected capptag: 0x{:0>02x}".format(error_snapshot_exp_tag))
			print (">> OpenCAPI dpart : ",error_snapshot_dp, " - OpenCAPI OW : ",error_snapshot_ow)
			print("-------------------------")
		else:
			print("Errors     :  no errors found ")

		run_high = fire.i2cread(0x01020000000000B0)
		#run_high =0x0000000000000000
		#print("RUN TIME H :",run_high)
		run_low = fire.i2cread(0x010200000000008C)
		#run_low = 0x00000000788F9D15
		#print("RUN TIME L :",run_low)

		run_time = (run_low + (run_high << 32)) / (fire.freq*1E6)
		print("Run Time   : {:.2f} sec".format(run_time))

		#Read latency for every engine
		lat_high = fire.i2cread(0x01020000000000B8)
		lat_low = fire.i2cread(0x01020000000000B4)
		latency_E0 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E0 : {:0>.2f} secs".format(latency_E0))

		lat_high = fire.i2cread(0x01020000000000CC)
		lat_low = fire.i2cread(0x01020000000000BC)
		latency_E1 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E1 : {:0>.2f} secs".format(latency_E1))

		lat_high = fire.i2cread(0x01020000000000D4)
		lat_low = fire.i2cread(0x01020000000000D0)
		latency_E2 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E2 : {:0>.2f} secs".format(latency_E2))

		lat_high = fire.i2cread(0x01020000000000DC)
		lat_low = fire.i2cread(0x01020000000000D8)
		latency_E3 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E3 : {:0>.2f} secs".format(latency_E3))

		lat_high = fire.i2cread(0x01020000000000E4)
		lat_low = fire.i2cread(0x01020000000000E0)
		latency_E4 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E4 : {:0>.2f} secs".format(latency_E4))

		lat_high = fire.i2cread(0x01020000000000EC)
		lat_low = fire.i2cread(0x01020000000000E8)
		latency_E5 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E5 : {:0>.2f} secs".format(latency_E5))

		lat_high = fire.i2cread(0x01020000000000F4)
		lat_low = fire.i2cread(0x01020000000000F0)
		latency_E6 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E6 : {:0>.2f} secs".format(latency_E6))

		lat_high = fire.i2cread(0x01020000000000FC)
		lat_low = fire.i2cread(0x01020000000000F8)
		latency_E7 = ((lat_low + (lat_high << 32)) / (fire.freq*1E6))
		print("Latency E7 : {:0>.2f} secs".format(latency_E7))

		latency = latency_E0 + latency_E1 + latency_E2 + latency_E3 + latency_E4 + latency_E5 + latency_E6 + latency_E7
		print("Sum of lat : {:0>.2f} secs".format(latency))

		nb_rd_high = fire.i2cread(0x01020000000000A8)
		#nb_rd_high =0x0000000000000000 
		#print("nb_rd H :",nb_rd_high)
		nb_rd_low  = fire.i2cread(0x010200000000007c)
		#nb_rd_low  =0x0000000015C3D72B
		#print("nb_rd L :",nb_rd_low)
		# MSB for reads are only 4 digits right
		nb_rd      = nb_rd_low + ((nb_rd_high & 0x0000FFFF) << 32)
		#print("Total reads  = 0x{:0>16x}<<32".format(nb_rd_high) + "+ 0x{:0>16x}".format(nb_rd_low) + "= 0x{:0>16x}".format(nb_rd))
		print("Total RD   :",nb_rd)		

		nb_32Brd_high = fire.i2cread(0x01020000000000AC)
		#nb_32Brd_high =0x0000000000000000
		#print("nb_32Brd H :",nb_32Brd_high)
 
		nb_32Brd_low  = fire.i2cread(0x0102000000000084)
		#nb_32Brd_low  =0x000000002B87AE56
		#print("nb_32Brd L :",nb_32Brd_low)

		# MSB for reads are only 4 digits right
		nb_32Brd      = nb_32Brd_low + ((nb_32Brd_high  & 0x0000FFFF)<< 32)
		print("nb 32B rd  :",nb_32Brd)

		if (nb_rd != 0 ):
			if (nb_32Brd/nb_rd == 2.0):
				print("Access is  : READ 64 Bytes")
			elif (nb_32Brd/nb_rd == 4.0):
				print("Access is  : READ 128 Bytes")
			else:
				print("Access is  : READ nb_32Brd/nb_rd Bytes!!")

		print("freq       :",fire.freq, "MHz")
		if (nb_rd != 0 ):
			avg_rd_lat = latency / nb_32Brd *1000000000
			print("Avg Rd lat : {:0>.2f} ns".format(avg_rd_lat))
		else:
			print("Avg Rd lat : NA")


		Throughput = nb_32Brd * 32 / run_time / 1000000000
		print("Throughput : {:0>.2f} GBps".format(Throughput))

		print("-------------------------")

	def reg_ops(self, reg_list, _busnum, _ddimm):
		fire = Fire(_busnum)
		logging.info(_ddimm)
		logging.info(reg_list[0])
		if _ddimm == "a":
			ddimm_add_adj=0x00000000
		elif _ddimm == "b":
			ddimm_add_adj=0x00000400
		else: 
			print("ERROR: incorrect ddimm selection !!")
		logging.info("{:d}".format(len(reg_list)//4) + " registers to be R/W:")
		
		for i in range(1, len(reg_list), 4):
			""" Address is computed with port, based on port0 address """
			reg=reg_list[i+1]+(ddimm_add_adj<<32)
			logging.info("0x{:0>16x}".format(reg))
			#print(reg_list[i+3])
			if reg_list[i] == 'R':
				if  (type(reg_list[i+2])  == str):
					#print("READ  REG: " + "0x{:0>16x}".format(reg) + " .  .  .  .  .  .  .  .  " + " READ: "  + "0x{:0>16x}".format(fire.i2cread(reg)))
					fire.i2cread(reg)
				else:
					#print("READ  REG: " + "0x{:0>16x}".format(reg) + " EXP : " + "0x{:0>16x}".format(reg_list[i+2]) + " READ: "  + "0x{:0>16x}".format(fire.i2cread(reg)))
					fire.i2cread(reg)
					if ("0x{:0>16x}".format(reg_list[i+2]) != "0x{:0>16x}".format(fire.i2cread(reg))):
						fire.i2cread(reg)
						print("!!! WARNING: READ DATA Not expected !!!!")
			else:
				#print("WRITE REG: " + "0x{:0>16x}".format(reg) + " DATA: " + "0x{:0>16x}".format(reg_list[i+2]));fire.i2cwrite(reg, reg_list[i+2])
				fire.i2cwrite(reg, reg_list[i+2])

if __name__ == "__main__":
	# logging.basicConfig(level=logging.INFO)
	fbist = Fbist()
