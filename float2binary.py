
#
# float2binary.py
#

import sys
import os
import math
import time

##################################################

def float2binarystring(f):
    binarystring = ''
    negativepower = 1.0

    for i in range(0, 16):
        negativepower = negativepower / 2.0

        if f > negativepower:
            binarystring += '1'
            f = f - negativepower
        else:
            binarystring += '0'

    return binarystring

##################################################

def binarystring2int(binarystring):
    print('---------------')
    v = 0
    print(binarystring)
    for i in range(0, len(binarystring)):
        v = v * 2
        if binarystring[i] == '1':
            v += 1

    print('0x{:02X}'.format(v))
    print('---------------')
    return v

##################################################

f = 354726.123456789
f = time.time()

intpart = int(math.floor(f))
fracpart = f - float(intpart)

print(f)
print(intpart)
print(fracpart)

milliseconds = int(math.floor(fracpart * 1000))

print(milliseconds)

fp = fracpart

negpower = 1.0
checkvalue = 0.0

binary = ''
for i in range(0, 16):
    negpower = negpower / 2.0
    # print(i, negpower)

    if fp > negpower:
        binary += '1'
        ### print('1', end='')
        fp = fp - negpower
        checkvalue += negpower
    else:
        binary += '0'
        ### print('0', end='')


print(binary)

v = binarystring2int(binary[0:8])

print(checkvalue)

sys.exit(0)


#
#  0.0000
#
#    0000
#    ....
#    521
#     52
#      5
#      
#  0.5  
#    