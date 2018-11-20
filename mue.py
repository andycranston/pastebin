#! /usr/bin/python3
#
# @(!--#) @(#) mue.py, version 006, 23-february-2018
#
# a modbus server emulator implemented over UDP
#
# for basic emulation / demo purposes
#
# initially developed to allow the 4NG demo SMARTset running on a laptop
# to see "real" emulated data
#
# runs "forever" - use Ctrl+Break instead of Ctrl^C to interrupt.
#
# so far supports function code 6 and function code 3 
#

##############################################################################

#
# Help from:
# ---------
#
#
# RTA Automation
#   https://www.rtaautomation.com/technologies/modbus-tcpip/
#
# Binary Tides
#   http://www.binarytides.com/programming-udp-sockets-in-python/
#   http://www.binarytides.com/python-socket-programming-tutorial/
#

##############################################################################

#
# imports
#

import sys
import os
import socket
import time

##############################################################################

#
# constants
#

MIN_PACKET_LENGTH = 8
COLUMN_WIDTH = 72

##############################################################################

#
# globals
#

registers = ([ 0 ] * 65536)

registers[0] = 0
registers[1] = 1
registers[2] = 43981
registers[3] = 12345
registers[4] = 1
registers[5] = 65535
registers[6] = 520
registers[7] = 20746
registers[8] = 0
registers[9] = 0

### print(registers)

##############################################################################

def showpacket(bytes):
    bpr = 16              # bpr is Bytes Per Row
    numbytes = len(bytes)

    if numbytes == 0:
        print("<empty packet>")
    else:
        i = 0
        while i < numbytes:
            if (i % bpr) == 0:
                print("{:04d} :".format(i), sep='', end='')

            print(" {:02X}".format(bytes[i]), sep='', end='')

            if ((i + 1) % bpr) == 0:
                print()

            i = i + 1

    if (numbytes % bpr) != 0:
        print()

##############################################################################

#
# Main code
#

# extract program name
progname = os.path.basename(sys.argv[0])

# extract number of arguments (ignoring program name)
numargs = len(sys.argv) - 1

# if an odd number of arguments then something wrong
if (numargs % 2) != 0:
    print(progname, ": odd number of command line arguments", sep='', file=sys.stderr)
    sys.exit(1)

# set program defaults
udpport = "8502"

# loop through command line args
arg = 1
while arg < numargs:
    if sys.argv[arg] == "-p":
        udpport = sys.argv[arg+1]
        if not udpport.isdigit():
            print(progname, ": port number must be all digits", sep='', file=sys.stderr)
            sys.exit(1)
    else:
        print(progname, ": unrecognised command line argument \"", sys.argv[arg], "\"", sep='', file=sys.stderr)
        sys.exit(1)
    arg = arg + 2

# print program globals
print("===", progname, "=" * (COLUMN_WIDTH - 5 - len(progname)))
print("Modbus UDP port number..:", udpport)
print("=" * COLUMN_WIDTH)

# create a TCP/IP socket for receiving DHCP packets on port 69
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# bind the socket to the port
sock.bind(('', int(udpport)))

# main loop for modbus UDP server
while True:
    # wait for a request
    print("")
    print("waiting for a Modbus request")
    try:
        modbusrequest, address = sock.recvfrom(32768)
    except ConnectionResetError:
        print(progname, ": recvfrom had a connection reset error - going again", sep='', file=sys.stderr)
        continue

    lenmodbusrequest = len(modbusrequest)
    clientip = address[0]
    clientport = address[1]

    # show the packet
    print("client IP:", clientip, "   TCP/IP port number:", clientport, "   packet size:", lenmodbusrequest)
    showpacket(modbusrequest)

    # if request too short then ignore
    if lenmodbusrequest < MIN_PACKET_LENGTH:
        print(progname, ": packet length too short (less than ", MIN_PACKET_LENGTH, " bytes) - ignoring", sep='', file=sys.stderr)
        continue

    # extract data length from packet itself (byte offsets 4 and 5)
    datalen = (modbusrequest[4] * 256) + modbusrequest[5]

    # does this data length make sense?
    if (datalen + 6) != lenmodbusrequest:
        print(progname, ": packet length mismatch - ", datalen, "+6 is not ", lenmodbusrequest, " - ignoring", sep='', file=sys.stderr)
        continue

    # extract function code
    fcode = modbusrequest[7]

    # deal with function code 03 - read multiple registers
    if fcode == 3:
        if datalen != 6:
            print(progname, ": function code 03 expects 6 bytes of data but got ", datalen, " bytes - ignoring", sep='', file=sys.stderr)
            continue

        regstart = (modbusrequest[8] * 256) + modbusrequest[9]
        regcount = (modbusrequest[10] * 256) + modbusrequest[11]

        if regcount == 0:
            print(progname, ": function code 03 has a register count of 0 which makes no sense - ignoring", sep='', file=sys.stderr)
            continue

        if (regstart + (regcount - 1)) > 65535:
            print(progname, ": function code 03 register start ", regstart, " plus register count ", regcount, " goes past 65535 array limit - ignoring", sep='', file=sys.stderr)
            continue

        lenmodbusresponse = 9 + (regcount * 2)
        modbusresponse = bytearray(lenmodbusresponse)

        modbusresponse[0:4] = modbusrequest[0:4]
        modbusresponse[4] = (3 + (regcount * 2)) // 256
        modbusresponse[5] = (3 + (regcount * 2)) % 256
        modbusresponse[6:8] = modbusrequest[6:8]
        modbusresponse[8] = regcount * 2

        i2 = 9
        for i in range(0, regcount):
            regvalue = registers[regstart + i]
            modbusresponse[i2] = regvalue // 256
            i2 += 1
            modbusresponse[i2] = regvalue % 256
            i2 += 1
            
        showpacket(modbusresponse)
        ### time.sleep(2)
        sent = sock.sendto(modbusresponse, address)

    # deal with function code 06 - write single register
    if fcode == 6:
        if datalen != 6:
            print(progname, ": function code 06 expects 6 bytes of data but got ", datalen, " bytes - ignoring", sep='', file=sys.stderr)
            continue

        regaddress = (modbusrequest[8] * 256) + modbusrequest[9]
        regvalue = (modbusrequest[10] * 256) + modbusrequest[11]

        registers[regaddress] = regvalue

        # function code 06 response is the request unmodified - easy :-]
        showpacket(modbusrequest)
        sent = sock.sendto(modbusrequest, address)

    # deal with function code 16 - write multiple registers
    if fcode == 16:
        if datalen < 9:
            print(progname, ": function code 16 expects 9 or more bytes of data but got ", datalen, " bytes - ignoring", sep='', file=sys.stderr)
            continue

        regstart = (modbusrequest[8] * 256) + modbusrequest[9]
        regcount = (modbusrequest[10] * 256) + modbusrequest[11]

        if regcount == 0:
            print(progname, ": function code 16 has a register count of 0 which makes no sense - ignoring", sep='', file=sys.stderr)
            continue

        if (regstart + (regcount - 1)) > 65535:
            print(progname, ": function code 16 register start ", regstart, " plus register count ", regcount, " goes past 65535 array limit - ignoring", sep='', file=sys.stderr)
            continue

        bytecount = modbusrequest[12]

        if bytecount != (regcount * 2):
            print(progname, ": function code 16 byte count ", bytecount, " is not twice register count ", regcount, " - ignoring", sep='', file=sys.stderr)
            continue

        i2 = 13
        while regcount > 0:
            registers[regstart] = (modbusrequest[i2] * 256) + modbusrequest[i2+1]
            i2 += 2
            regcount -= 1

        lenmodbusresponse = 9 + (regcount * 2)
        modbusresponse = bytearray(lenmodbusresponse)

        modbusresponse[0:4] = modbusrequest[0:4]
        modbusresponse[4] = 0
        modbusresponse[5] = 12
        modbusresponse[6:12] = modbusrequest[6:12]

        showpacket(modbusresponse)
        ### time.sleep(2)
        sent = sock.sendto(modbusresponse, address)

sys.exit(0)

# end of file
