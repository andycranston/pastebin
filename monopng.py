#
# monopng.py, version 001, 07-march-2017
#
# create a monochrome png file
#

import zlib

##############################################################################

def dword(i):
###    print("i=", i)

    b0 = (i & 0x000000FF) // 0x00000001
    b1 = (i & 0x0000FF00) // 0x00000100
    b2 = (i & 0x00FF0000) // 0x00010000
    b3 = (i & 0xFF000000) // 0x01000000

###    print("B0 = ", b0)
###    print("B1 = ", b1)
###    print("B2 = ", b2)
###    print("B3 = ", b3)

    return bytes([b3, b2, b1, b0])

##############################################################################

def monopng(f, bitmap):
    height = len(bitmap)
    width = len(bitmap[0])
    bitdepth = 8             # one byte per pixel
    colourtype = 0           # true grayscale (no palette)
    compression = 0          # zlib
    filtertype = 0           # adaptive (each scanline seperately)
    interlaced = 0           # no interlacing

###    print("Height.......: ", height)
###    print("Width........: ", width)

    # create png header
    png = b"\x89" + "PNG\r\n\x1A\n".encode('ascii')

    # create and add IHDR
    data = b""

    data += dword(width) + dword(height)
    data += bytes([bitdepth])
    data += bytes([colourtype])
    data += bytes([compression])
    data += bytes([filtertype])
    data += bytes([interlaced])

###    print("Length of IHDR data is ", len(data))
###    print(data)

    block = "IHDR".encode('ascii') + data

    png += dword(len(data)) + block + dword(zlib.crc32(block))

    # create and add IDAT
    data = b""

    for row in range(height):
###        print("ROW=", bitmap[row])

        data += b"\0"

        for col in range(len(bitmap[row])):
            pixel = b"\xFF"   # assume black pixel

            if bitmap[row][col] == "1":
                pixel = b"\x00"   # white pixel

            data += pixel

    compressor = zlib.compressobj()
    compressed = compressor.compress(data)
    compressed += compressor.flush()       #!! what!?

    block = "IDAT".encode('ascii') + compressed

    png += dword(len(compressed)) + block + dword(zlib.crc32(block))

    # create and add IEND
    data = b""

    block = "IEND".encode('ascii') + data

    png += dword(len(data)) + block + dword(zlib.crc32(block))

    # write the PNG data out to the file
    f.write(png)

    return

##############################################################################

#
# end of file
#
