#!/usr/bin/env python3

import sys, binascii
import serial


"""
   args[0] = this script
   args[1] = cmd [sndbyts|sndstr]
   args[2] = ttyUSBx
   args[3] = modbus adrs
   args[4] = bytes  00,32,23,xx,xx,xx 
"""

CMDS = ["SNDBYTES", "SNDSTR"]
if sys.argv[1].upper() not in CMDS:
   print(f"\nband cmd: {sys.argv[1]}")
   exit(0)

CMD = sys.argv[1]
ttydev = sys.argv[2]
mbadr = int(sys.argv[3])
bufstr = sys.argv[4]
print(f"\n\t--- running {CMD} ---")

buff: bytearray = bytearray()
for x in sys.argv[3].split(","):
   n: int = int(x, 16)
   buff.append(n)

port: serial.Serial = serial.Serial(port=ttydev)
print(f"\nserial sending: {buff}\n")
port.write(buff)
