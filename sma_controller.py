#!/usr/bin/env python

"""
SMA_SunnyIslandController: Reading out and controlling a SMA Sunny Island 8.0-13 (battery storage)

MIT License

Copyright (c) 2020 Harm van den Brink

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__author__  = 'Harm van den Brink'
__email__   = 'harmvandenbrink@gmail.com'
__license__ = 'MIT License'

__version__ = '0.0.1'
__status__  = 'Beta'

import sunspec.core.client as clientSunspec
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.compat import iteritems
from collections import OrderedDict

modbusInverterIP = '192.168.0.0'

# Change these values to match your connection, DSO regulation and system as a whole. Be careful changing them, only higher them if you are really sure.
maxChargeValue = -2000
maxDischargeValue = 2000
#

# The modbus registers to activate the communication and the power control address
activateControlAddress = 40151
changePowerAddress = 40149
#

try:
	# Controlling the battery via SunSpec showed some issues, thus SunSpec is only used to read out the battery
	# Slave ID is 126 because this is the SunSpec Slave ID
	sunSpecClient = clientSunspec.SunSpecClientDevice(clientSunspec.TCP, 126, ipaddr=modbusInverterIP, ipport=502, timeout=2.0)
except:
	print("Error connecting to the inverter via SunSpec")

try:
	# Slave ID is 3 because this is the right ID for controlling the charge/discharge power
	modbusClient = ModbusClient(modbusInverterIP, port=502, unit_id=3 , auto_open=True, auto_close=True)
except:
	print("Error connecting to the inverter via plain Modbus")
	
def readSMAValues():
	sunSpecClient.common.read()
	sunSpecClient.nameplate.read()
	sunSpecClient.status.read()
	sunSpecClient.controls.read()
	sunSpecClient.inverter.read()
	sunSpecClient.storage.read()

	sma = OrderedDict([
			('Mn', sunSpecClient.common.Mn),
			('Md', sunSpecClient.common.Md),
			('Opt', sunSpecClient.common.Opt),
			('Vr', sunSpecClient.common.Vr),
			('SN', sunSpecClient.common.SN),
			('DERTyp', sunSpecClient.nameplate.DERTyp),
			('WRtg', sunSpecClient.nameplate.WRtg),
			('WHRtg', sunSpecClient.nameplate.WHRtg),
			('AhrRtg', sunSpecClient.nameplate.AhrRtg),
			('MaxChaRte', sunSpecClient.nameplate.MaxChaRte),
			('MaxDisChaRte', sunSpecClient.nameplate.MaxDisChaRte),
			('PVConn', sunSpecClient.status.PVConn),
			('StorConn', sunSpecClient.status.StorConn),
			('ECPConn', sunSpecClient.status.ECPConn),
			('ActWh', sunSpecClient.status.ActWh),
			('WMaxLimPct', sunSpecClient.controls.WMaxLimPct),
			('WMaxLim_Ena', sunSpecClient.controls.WMaxLim_Ena),
			('OutPFSet_Ena', sunSpecClient.controls.OutPFSet_Ena),
			('VArPct_Mod', sunSpecClient.controls.VArPct_Mod),
			('VArPct_Ena', sunSpecClient.controls.VArPct_Ena),
			('AphA', sunSpecClient.inverter.AphA),
			('AphB', sunSpecClient.inverter.AphB),
			('AphC', sunSpecClient.inverter.AphC),
			('PhVphA', sunSpecClient.inverter.PhVphA),
			('PhVphB', sunSpecClient.inverter.PhVphB),
			('W', sunSpecClient.inverter.W),
			('Hz', sunSpecClient.inverter.Hz),
			('VAr', sunSpecClient.inverter.VAr),
			('WH', sunSpecClient.inverter.WH),
			('Evt1', sunSpecClient.inverter.Evt1),
			('WChaMax', sunSpecClient.storage.WChaMax),
			('StorCtl_Mod', sunSpecClient.storage.StorCtl_Mod),
			('ChaState', sunSpecClient.storage.ChaState),
			('InBatV', sunSpecClient.storage.InBatV),
			('ChaSt', sunSpecClient.storage.ChaSt),
	])
	return sma

def limitPower(num, minimum=maxChargeValue, maximum=maxDischargeValue):
	return int(max(min(num, maximum), minimum))

def sendModbus(address, value, type):
	global modbusClient
	if(modbusClient.connect() == False):
		print("Modbus connection lost, trying to reconnect...")
		ModbusClient(modbusInverterIP, port=502, unit_id=3 , auto_open=True, auto_close=True)
		print("Modbus Connected: {}".format(modbusClient.connect()))
	else:
		# SMA expects everything in Big Endian format
		builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
		# Only unsigned int32 and signed int32 are built in. It is enough to control the flow of power of the battery.
		if (type == "uint32"):
			builder.add_32bit_uint(value)
		if (type == "int32"):
			builder.add_32bit_int(value)
		registers = builder.to_registers()
		modbusClient.write_registers(address, registers, unit=3)
	
def changePowerOfTheInverter(power):
	# 40149 Active power setpoint - int32
	# 40151 Eff./reac. pow. contr. via comm. 802 = "active" 803 = "inactive", ENUM - uint32
	# 40153 Reactive power setpoint - uint32
	# 0x0322 is the value (802) to activate the control of power via modbus communication
	sendModbus(activateControlAddress, 0x0322, "uint32")
	sendModbus(changePowerAddress, limitPower(power), "int32")

#sma = readSMAValues('ChaState')
#print(sma)

# A positive value means it'll feed back into the grid, a negative number means it'll take energy from the grid.
#changePowerOfTheInverter(1000)
#changePowerOfTheInverter(-1500)