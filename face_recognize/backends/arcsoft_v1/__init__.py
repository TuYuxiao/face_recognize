# -*- encoding=utf-8 -*-

from ctypes import *


class ASVLOFFSCREEN(Structure):
    _fields_ = [('u32PixelArrayFormat', c_uint32), ('i32Width', c_int32), ('i32Height', c_int32),
                ('ppu8Plane', POINTER(c_ubyte) * 4), ('pi32Pitch', c_int32 * 4)]

    def __init__(self):
        Structure.__init__(self)
        self.gc_ppu8Plane0 = None
        self.gc_ppu8Plane1 = None
        self.gc_ppu8Plane2 = None
        self.gc_ppu8Plane3 = None


class MRECT(Structure):
    _fields_ = [('left', c_int32), ('top', c_int32), ('right', c_int32), ('bottom', c_int32)]
