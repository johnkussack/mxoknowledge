from binarywalker import *
from objmodel import *
import zlib

from PIL import Image

class FileFormat:
    DXT1 = 1
    DXT3 = 3
    DXT5 = 5
    A8R8G8B8 = 0xA8,
    G8 = 0x68

class PixelFormatFlags:
    FourCC = 0x00000004
    RGB = 0x00000040
    RGBA = 0x00000041
    Gray = 0x00020000

class HeaderFlags:
    hNone = 0x00000000
    Texture = 0x00001007
    MipMap = 0x00020000
    Volume = 0x00800000
    Pitch = 0x00000008
    LinearSize = 0x00080000

class SurfaceFlags :
    sNone = 0x00000000
    Texture = 0x00001000
    MipMap = 0x00400008
    CubeMap = 0x00000008

class PixelFormat():
    def __init__(self, ddsVersion):

        self.size = 8*4

        """
        FourCC = 0x00000004,
        RGB    = 0x00000040,
        RGBA   = 0x00000041,
        Gray = 0x00020000
        """
        if ddsVersion in [FileFormat.DXT1, FileFormat.DXT3, FileFormat.DXT5]:
            self.flags = PixelFormatFlags.FourCC
            self.rgbBitCount = 0
            self.rBitMask = 0
            self.gBitMask = 0
            self.bBitMask = 0
            self.aBitMask = 0

            if ddsVersion == FileFormat.DXT1:
                self.fourCC = bytes.fromhex("44585431")  # "DXT1"
            elif ddsVersion == FileFormat.DXT3:
                self.fourCC = bytes.fromhex("44585433")  # "DXT3"
            elif ddsVersion == FileFormat.DXT5:
                self.fourCC = bytes.fromhex("44585435")  # "DXT5"
        elif ddsVersion == FileFormat.A8R8G8B8:
            self.flags = PixelFormatFlags.RGBA
            self.fourCC = bytes.fromhex("00000000")  # Zero
            self.rgbBitCount = 32
            self.rBitMask = 0x00ff0000
            self.gBitMask = 0x0000ff00
            self.bBitMask = 0x000000ff
            self.aBitMask = 0xff000000
        elif ddsVersion == FileFormat.G8:
            self.flags = PixelFormatFlags.Gray
            self.fourCC = bytes.fromhex("00000000")  # Zero
            self.rgbBitCount = 8

            self.rBitMask = 0x000000ff
            self.gBitMask = 0x00000000
            self.bBitMask = 0x00000000
            self.aBitMask = 0x00000000



    def to_hex(self):
        result = bytearray()
        result += struct.pack("I", self.size)
        result += struct.pack("I", self.flags)
        result += self.fourCC
        result += struct.pack("I", self.rgbBitCount)
        result += struct.pack("I", self.rBitMask)
        result += struct.pack("I", self.gBitMask)
        result += struct.pack("I", self.bBitMask)
        result += struct.pack("I", self.aBitMask)
        return result


class DdsHeader:

    def __init__(self, width, height, ddsVersion):

        self.pixelFormat = PixelFormat(ddsVersion)
        self.isCompressed = (ddsVersion in [FileFormat.DXT1, FileFormat.DXT3, FileFormat.DXT5]) # always yes?
        self.height = height
        self.width = width

        mipCount = self.countMipMaps(self.width, self.height)

        self.size = 18*4 + self.pixelFormat.size + 5 * 4



        if mipCount == 1:
            self.mipMapCount = 0
        else:
            self.mipMapCount = mipCount

        # header flags
        self.headerFlags = HeaderFlags.Texture
        if self.isCompressed:
            self.headerFlags = self.headerFlags | HeaderFlags.LinearSize
        else:
            self.headerFlags = self.headerFlags | HeaderFlags.Pitch

        if mipCount>1:
            self.headerFlags = self.headerFlags | HeaderFlags.MipMap
        else:
            self.headerFlags = self.headerFlags | HeaderFlags.hNone

        # surface flags
        self.surfaceFlags = SurfaceFlags.Texture
        if mipCount>1:
            self.surfaceFlags = self.surfaceFlags | SurfaceFlags.MipMap
        else:
            self.surfaceFlags = self.surfaceFlags | SurfaceFlags.sNone

        if self.isCompressed: # Most DXT stuff
            blockCount = (width+3) / 4.0* ((height+3)/4.0)
            blockSize = 16
            self.pitchOrLinearSize = int(blockCount*blockSize)
        else:
            pixelWidth = 0
            if ddsVersion == FileFormat.A8R8G8B8:
                pixelWidth = 4

            elif ddsVersion == FileFormat.G8:
                pixelWidth = 1

            self.pitchOrLinearSize = self.width * pixelWidth

        # not initialized
        self.depth = 0
        self.reserved = bytes.fromhex("00"*4*11)
        self.cubemapFlags = 0
        self.reserved2 = bytes.fromhex("00"*4 * 3)


    def countMipMaps(self, width, height):
        mipCount = 1
        w = width
        h = height

        while(w>1 or h>1):
            mipCount+=1

            if(w>1) : w /= 2.0
            if(h>1): h /= 2.0
        return mipCount


    def to_hex(self):
        header = bytearray()
        header += struct.pack("I", self.size)
        header += struct.pack("I", self.headerFlags)
        header += struct.pack("I",self.height)
        header += struct.pack("I",self.width)
        header += struct.pack("I", self.pitchOrLinearSize)
        header += struct.pack("I", self.depth)


        header += struct.pack("I", self.mipMapCount)

        header += self.reserved
        header += self.pixelFormat.to_hex()
        header += struct.pack("I", self.surfaceFlags)
        header += struct.pack("I", self.cubemapFlags)
        header += self.reserved2


        return header


class DssParser:

    @staticmethod
    def parse_file(file_name):

        with open(file_name, "rb") as f:
            data = f.read()
        b = BinaryWalker()
        b.setData(data)

        # parsing start
        header_size = b.getInt16()
        b.seek(header_size) # skip header content for now

        image_and_header_size = b.getInt32()

        unknown_1 = b.getInt32()  # Must be description or part for data compression

        dds_type_maybe = b.getInt16()
        print("Type is: ", hex(dds_type_maybe))

        dds_version = FileFormat.DXT1
        if dds_type_maybe == 0x0e:
            print("Detected DXT5")
            dds_version = FileFormat.DXT5
        elif dds_type_maybe == 0x0d:
            print("Detected DXT3")
            dds_version = FileFormat.DXT3
        elif dds_type_maybe == 0x0c:
            print("Detected DXT1")
            dds_version = FileFormat.DXT1
        elif dds_type_maybe == 0x01:
            print("Detected A8R8G8B8?")
            dds_version = FileFormat.A8R8G8B8
        else:
            print("Unknown format!!")

        unknown_3 = b.getInt16()  # Must be description or part for data compression

        width = b.getInt16()
        height = b.getInt16()

        unknown_4 = b.getInt16() # Must be description or part for data compression ???

        real_data_size = len(data) - b.offset
        real_data_bytes = b.getBlob(real_data_size)

        header = DdsHeader(width, height, dds_version)

        hdata =(bytearray("DDS ","ascii"))
        hdata += header.to_hex()
        hdata += real_data_bytes
        return hdata

