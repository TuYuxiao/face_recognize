# -*- encoding=utf-8 -*-
import platform
import os
from ctypes import *
from . import ASVLOFFSCREEN, MRECT
from face_recognize.common import ArcsoftFaceFeature


class AFR_FSDK_Version(Structure):
    _fields_ = [('lCodebase', c_int32), ('lMajor', c_int32), ('lMinor', c_int32), ('lBuild', c_int32),
                ('lFeatureLevel', c_int32),
                ('Version', c_char_p), ('BuildDate', c_char_p), ('CopyRight', c_char_p)]


class AFR_FSDK_FACEINPUT(Structure):
    _fields_ = [('rcFace', MRECT), ('lOrient', c_int32)]

    def __init__(self):
        Structure.__init__(self)
        # self.faceRect = self.rcFace
        # self.faceOrient = lOrient


class AFR_FSDK_FACEMODEL(ArcsoftFaceFeature):
    _fields_ = [('pbFeature', c_void_p), ('lFeatureSize', c_int32)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _feature(self):
        return self.pbFeature

    @_feature.setter
    def _feature(self, feature):
        self.pbFeature = feature

    @property
    def feature_size(self):
        return self.lFeatureSize

    @feature_size.setter
    def feature_size(self, feature_size):
        self.lFeatureSize = feature_size


default_lib_path = os.path.expanduser("~/.face_recognize/lib")

if platform.system() == 'Windows':
    internalLibraryPath = os.path.join(default_lib_path, 'libarcsoft_fsdk_face_recognition.dll')
else:
    internalLibraryPath = os.path.join(default_lib_path, 'libarcsoft_fsdk_face_recognition.so')

if not os.path.exists(internalLibraryPath):
    print("Please download %s from Arcsoft face recognition platform and move them to ~/.face_recognize/lib " % (
        os.path.basename(internalLibraryPath)))

internalLibrary = CDLL(internalLibraryPath)

AFR_FSDK_InitialEngine = internalLibrary.AFR_FSDK_InitialEngine
AFR_FSDK_UninitialEngine = internalLibrary.AFR_FSDK_UninitialEngine
AFR_FSDK_ExtractFRFeature = internalLibrary.AFR_FSDK_ExtractFRFeature
AFR_FSDK_FacePairMatching = internalLibrary.AFR_FSDK_FacePairMatching
AFR_FSDK_GetVersion = internalLibrary.AFR_FSDK_GetVersion

AFR_FSDK_InitialEngine.restype = c_long
AFR_FSDK_InitialEngine.argtypes = (c_char_p, c_char_p, c_void_p, c_int32, POINTER(c_void_p))
AFR_FSDK_UninitialEngine.restype = c_long
AFR_FSDK_UninitialEngine.argtypes = (c_void_p,)
AFR_FSDK_ExtractFRFeature.restype = c_long
AFR_FSDK_ExtractFRFeature.argtypes = (
c_void_p, POINTER(ASVLOFFSCREEN), POINTER(AFR_FSDK_FACEINPUT), POINTER(AFR_FSDK_FACEMODEL))
AFR_FSDK_FacePairMatching.restype = c_long
AFR_FSDK_FacePairMatching.argtypes = (
c_void_p, POINTER(AFR_FSDK_FACEMODEL), POINTER(AFR_FSDK_FACEMODEL), POINTER(c_float))
AFR_FSDK_GetVersion.restype = POINTER(AFR_FSDK_Version)
AFR_FSDK_GetVersion.argtypes = (c_void_p,)
