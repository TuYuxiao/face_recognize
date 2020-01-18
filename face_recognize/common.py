from ctypes import *
import platform

if platform.system() == 'Windows':
    internalLibrary = cdll.msvcrt
else:
    internalLibrary = CDLL('libc.so.6')

malloc = internalLibrary.malloc
free = internalLibrary.free
memcpy = internalLibrary.memcpy

malloc.restype = c_void_p
malloc.argtypes = (c_size_t,)
free.restype = None
free.argtypes = (c_void_p,)
memcpy.restype = c_void_p
memcpy.argtypes = (c_void_p, c_void_p, c_size_t)


class MPOINT(Structure):
    _fields_ = [('x', c_int32), ('y', c_int32)]


class MRECT(Structure):
    _fields_ = [('left', c_int32), ('top', c_int32), ('right', c_int32), ('bottom', c_int32)]


class ASVLOFFSCREEN(Structure):
    _fields_ = [('u32PixelArrayFormat', c_uint32), ('i32Width', c_int32), ('i32Height', c_int32),
                ('ppu8Plane', POINTER(c_ubyte) * 4), ('pi32Pitch', c_int32 * 4)]

    def __init__(self):
        Structure.__init__(self)
        self.gc_ppu8Plane0 = None
        self.gc_ppu8Plane1 = None
        self.gc_ppu8Plane2 = None
        self.gc_ppu8Plane3 = None


class FaceInfo:
    NAME_MAP = {}

    def __init__(self, orient, left, top, right, bottom, face_id=None):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.orient = orient
        self.face_id = face_id
        self.name = 'unknown'

    def __repr__(self):
        return 'FaceInfo[%s,%s,%s,%s]' % (self.left, self.right, self.top, self.bottom)


class FaceFeature(Structure):
    def __init__(self):
        Structure.__init__(self)
        self.allocByMalloc = False

    def getFeature(self):
        raise NotImplementedError()

    def setFeature(self, feature):
        raise NotImplementedError()

    def getFeatureSize(self):
        raise NotImplementedError()

    def setFeatureSize(self, featureSize):
        raise NotImplementedError()

    def copy(self):
        if (self.getFeature() == 0):
            raise Exception('invalid feature')
        feature_copy = self.__class__()
        feature_copy.allocByMalloc = True
        feature_copy.setFeatureSize(self.getFeatureSize())
        feature_copy.setFeature(malloc(feature_copy.getFeatureSize()))
        memcpy(feature_copy.getFeature(), self.getFeature(), self.getFeatureSize())
        return feature_copy

    def freeUnmanaged(self):
        if self.allocByMalloc and (self.getFeature() != 0):
            free(self.getFeature())
            self.setFeature(0)

    def __del__(self):
        self.freeUnmanaged()

    @classmethod
    def fromByteArray(cls, byteArrayFeature):
        if byteArrayFeature == None:
            raise Exception('invalid byteArray')
        feature = cls()
        feature.setFeatureSize(len(byteArrayFeature))
        feature.allocByMalloc = True
        featureData = create_string_buffer(byteArrayFeature)
        feature.setFeature(malloc(feature.getFeatureSize()))
        memcpy(feature.getFeature(), cast(featureData, c_void_p), feature.getFeatureSize())
        return feature

    def toByteArray(self):
        if (self.getFeature() == 0):
            raise Exception('invalid feature')
        featureData = create_string_buffer(self.getFeatureSize())
        memcpy(cast(featureData, c_void_p), self.getFeature(), self.getFeatureSize())
        return bytes(bytearray(featureData))
