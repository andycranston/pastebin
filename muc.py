#! /usr/bin/python3
#
# @(!--#) @(#) muc.py, version 003, 23-february-2018
#
# a modbus client implemented over UDP
#
# for basic testing of a Modbus UDP server
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

DEFAULT_COMMAND_FILENAME = "muc.cmd"
INFO_PREFIX = "INFO"
MIN_PACKET_LENGTH = 8
COLUMN_WIDTH = 72

##############################################################################

#
# globals
#


reqid = 65535
lastreply = bytearray(1)

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

def readregisters(server, port, unitid, reg, count):
    global reqid
    global lastreply

    print(INFO_PREFIX, ": reading ", count, " registers starting at ", reg, sep='')
    ### print(server, port, unitid, reg, count)

    reqid += 1
    if reqid > 65535:
        reqid = 0

    packet = bytearray(12)

    # request id
    packet[0] = reqid // 256
    packet[1] = reqid % 256
    # protocol (always 0)
    packet[2] = 0
    packet[3] = 0
    # length
    packet[4] = 0
    packet[5] = 6
    # unit id
    packet[6] = unitid
    # function code
    packet[7] = 3
    # register
    packet[8] = reg // 256
    packet[9] = reg % 256
    # count
    packet[10] = count // 256
    packet[11] = count % 256

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.settimeout(5.0)

    ### print("sending read request")
    ### showpacket(packet)
    s.sendto(packet,(server, port))

    ### print("waiting for reply")
    try:
        d = s.recvfrom(1024)
    except ConnectionResetError:
        print(progname, ": connection reset error", sep='', file=sys.stderr)
        s.close()
        return
    except socket.timeout:
        print(progname, ": timeout error", sep='', file=sys.stderr)
        s.close()
        return

    reply = d[0]
    addr = d[1]

    ### showpacket(reply)

    lastreply = reply    

    s.close()

##############################################################################

def write1register(server, port, unitid, reg, word):
    global reqid
    global lastreply

    print(INFO_PREFIX, ": writing register ", reg, " with word value ", word, sep='')
    ### print(server, port, unitid, reg, word)

    reqid += 1
    if reqid > 65535:
        reqid = 0

    packet = bytearray(12)

    # request id
    packet[0] = reqid // 256
    packet[1] = reqid % 256
    # protocol (always 0)
    packet[2] = 0
    packet[3] = 0
    # length
    packet[4] = 0
    packet[5] = 6
    # unit id
    packet[6] = unitid
    # function code
    packet[7] = 6
    # register
    packet[8] = reg // 256
    packet[9] = reg % 256
    # word
    packet[10] = word // 256
    packet[11] = word % 256

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.settimeout(5.0)

    ### print("sending write request")
    ### showpacket(packet)
    s.sendto(packet,(server, port))

    ### print("waiting for reply")
    try:
        d = s.recvfrom(1024)
    except ConnectionResetError:
        print(progname, ": connection reset error", sep='', file=sys.stderr)
        s.close()
        return
    except socket.timeout:
        print(progname, ": timeout error", sep='', file=sys.stderr)
        s.close()
        return

    reply = d[0]
    addr = d[1]

    ### showpacket(reply)

    lastreply = reply    

    s.close()

##############################################################################

def showreply():
    global lastreply

    showpacket(lastreply)

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
cmdfilename = DEFAULT_COMMAND_FILENAME
server = "127.0.0.1"
port = 8502
unitid = 0
reg = 0
count = 1
word = 0

# loop through command line args
arg = 1
while arg < numargs:
    if sys.argv[arg] == "-f":
        cmdfilename = sys.argv[arg+1]
    else:
        print(progname, ": unrecognised command line argument \"", sys.argv[arg], "\"", sep='', file=sys.stderr)
        sys.exit(1)
    arg = arg + 2

# print program globals
print("===", progname, "=" * (COLUMN_WIDTH - 5 - len(progname)))
print("Command filename...:", cmdfilename)
print("=" * COLUMN_WIDTH)

# open the command file for reading
try:
    cmdfile = open(cmdfilename, "r")
except OSError:
    print(progname, ": cannot open file \"", cmdfilename, "\" for reading - exiting", sep='', file=sys.stderr)
    sys.exit(1)


# for each file in the command file
linenum = 0
explicitexit = False
for line in cmdfile:
    linenum += 1
    line = line.strip()

    if len(line) == 0:
        continue
    if line[0] == '#':
        continue

    fields = line.split()
    numfields = len(fields)
    if numfields == 0:
        continue

    cmd = fields[0]

    # exit
    if cmd == "exit":
        print(INFO_PREFIX, ": explicit exit at line number ", linenum, sep='')
        explicitexit = True
        break

    # sleep
    if cmd == "sleep":
        if numfields < 2:
            print(progname, ": expected seconds command after sleep command", sep='', file=sys.stderr)
        else:
            seconds = float(fields[1])
            print(INFO_PREFIX, ": sleeping for ", seconds, " seconds", sep='')
            time.sleep(seconds)
        continue

    # server
    if cmd == "server":
        if numfields < 2:
            print(progname, ": expected server name/IP address after server command", sep='', file=sys.stderr)
        else:
            server = fields[1]
            print(INFO_PREFIX, ": server set to (", server, ")", sep='')
        continue

    # port
    if cmd == "port":
        if numfields < 2:
            print(progname, ": expected port number after port command", sep='', file=sys.stderr)
        else:
            port = int(fields[1])
            print(INFO_PREFIX, ": port set to (", port, ")", sep='')
        continue

    # unitid
    if cmd == "unitid":
        if numfields < 2:
            print(progname, ": expected unit ID after unitid command", sep='', file=sys.stderr)
        else:
            unitid = int(fields[1])
            print(INFO_PREFIX, ": unit ID set to (", unitid, ")", sep='')
        continue

    # reg
    if cmd == "reg":
        if numfields < 2:
            print(progname, ": expected register number after reg command", sep='', file=sys.stderr)
        else:
            reg = int(fields[1])
            print(INFO_PREFIX, ": register number set to (", reg, ")", sep='')
        continue

    # count
    if cmd == "count":
        if numfields < 2:
            print(progname, ": expected count value after count command", sep='', file=sys.stderr)
        else:
            count = int(fields[1])
            print(INFO_PREFIX, ": count value set to (", count, ")", sep='')
        continue

    # word
    if cmd == "word":
        if numfields < 2:
            print(progname, ": expected value after word command", sep='', file=sys.stderr)
        else:
            word = int(fields[1])
            print(INFO_PREFIX, ": word value set to (", word, ")", sep='')
        continue

    # read
    if cmd == "read":
        if numfields < 2:
            print(progname, ": expected keyword after read command", sep='', file=sys.stderr)
        else:
            keyword = (fields[1])
            if keyword == "reg":
                readregisters(server, port, unitid, reg, count)
            else:
                print(progname, ": line: ", linenum, ": unrecognised keyword ", keyword, " after read command", sep='', file=sys.stderr)
        continue

    # write
    if cmd == "write":
        if numfields < 2:
            print(progname, ": expected keyword after write command", sep='', file=sys.stderr)
        else:
            keyword = (fields[1])
            if keyword == "reg":
                write1register(server, port, unitid, reg, word)
            else:
                print(progname, ": line: ", linenum, ": unrecognised keyword ", keyword, " after write command", sep='', file=sys.stderr)
        continue

    # show
    if cmd == "show":
        if numfields < 2:
            print(progname, ": line: ", linenum, ": expected keyword after show command", sep='', file=sys.stderr)
        else:
            keyword = (fields[1])
            if keyword == "reply":
                showreply()
            else:
                print(progname, ": line: ", linenum, ": unrecognised keyword ", keyword, " after show command", sep='', file=sys.stderr)
        continue

    print(progname, ": unrecognised command (", cmd, ") at line number ", linenum, " - ignoring", sep='', file=sys.stderr)

# if implicit exit because of eof then say so
if explicitexit == False:
    print(INFO_PREFIX, ": implicit exit due to end of command file", sep='')


# close the command file
cmdfile.close()

# exit
sys.exit(0)

# end of file
