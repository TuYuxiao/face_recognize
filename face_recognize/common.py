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


class FaceInfo:
    def __init__(self, orient, left, top, right, bottom, face_id=None):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.orient = orient
        self.face_id = face_id
        self.name = None

    def __repr__(self):
        return 'FaceInfo[%s,%s,%s,%s]' % (self.left, self.right, self.top, self.bottom)


class FaceFeature:
    @classmethod
    def fromByteArray(cls, byteArrayFeature):
        raise NotImplementedError()

    def toByteArray(self):
        raise NotImplementedError()


class ArcsoftFaceFeature(FaceFeature, Structure):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allocByMalloc = False

    @property
    def _feature(self):
        raise NotImplementedError()

    @_feature.setter
    def _feature(self, feature):
        raise NotImplementedError()

    @property
    def feature_size(self):
        raise NotImplementedError()

    @feature_size.setter
    def feature_size(self, feature_size):
        raise NotImplementedError()

    def copy(self):
        if self._feature is None:
            raise Exception('invalid feature')
        feature_copy = self.__class__()
        feature_copy.allocByMalloc = True
        feature_copy.feature_size = self.feature_size
        feature_copy._feature = malloc(feature_copy.feature_size)
        memcpy(feature_copy._feature, self._feature, self.feature_size)
        return feature_copy

    def freeUnmanaged(self):
        if self.allocByMalloc and (self._feature is not None):
            free(self._feature)
            self._feature = None

    def __del__(self):
        self.freeUnmanaged()

    @classmethod
    def fromByteArray(cls, byteArrayFeature):
        if byteArrayFeature is None:
            raise Exception('invalid byteArray')
        feature = cls()
        feature.feature_size = len(byteArrayFeature)
        feature.allocByMalloc = True
        featureData = create_string_buffer(byteArrayFeature)
        feature._feature = malloc(feature.feature_size)
        memcpy(feature._feature, cast(featureData, c_void_p), feature.feature_size)
        return feature

    def toByteArray(self):
        if self._feature is None:
            raise Exception('invalid feature')
        featureData = create_string_buffer(self.feature_size)
        memcpy(cast(featureData, c_void_p), self._feature, self.feature_size)
        return bytes(bytearray(featureData))
