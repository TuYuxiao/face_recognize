import platform
import os
from ctypes import *
from face_recognize.common import MRECT, ASVLOFFSCREEN

class AFT_FSDK_FACERES(Structure):
    _fields_ = [('nFace',c_int32),('rcFace',POINTER(MRECT)),('lfaceOrient',c_int32)]

class AFT_FSDK_Version(Structure):
    _fields_ = [('lCodebase',c_int32),('lMajor',c_int32),('lMinor',c_int32),('lBuild',c_int32),
                ('Version',c_char_p),('BuildDate',c_char_p),('CopyRight',c_char_p)]

AFT_FSDK_OPF_0_ONLY = 0x1;       # 0; 0; ...
AFT_FSDK_OPF_90_ONLY = 0x2;      # 90; 90; ...
AFT_FSDK_OPF_270_ONLY = 0x3;     # 270; 270; ...
AFT_FSDK_OPF_180_ONLY = 0x4;     # 180; 180; ...
AFT_FSDK_OPF_0_HIGHER_EXT = 0x5; # 0; 90; 270; 180; 0; 90; 270; 180; ...

AFT_FSDK_FOC_0 = 0x1;# 0 degree
AFT_FSDK_FOC_90 = 0x2;  # 90 degree
AFT_FSDK_FOC_270 = 0x3; # 270 degree
AFT_FSDK_FOC_180 = 0x4; # 180 degree

if platform.system() == 'Windows':
    internalLibrary = CDLL(os.path.join(os.path.dirname(
        __file__), 'lib', 'libarcsoft_fsdk_face_tracking.dll'))
else:
    internalLibrary = CDLL(os.path.join(os.path.dirname(
        __file__), 'lib', 'libarcsoft_fsdk_face_tracking.so'))

AFT_FSDK_InitialFaceEngine = internalLibrary.AFT_FSDK_InitialFaceEngine
AFT_FSDK_UninitialFaceEngine = internalLibrary.AFT_FSDK_UninitialFaceEngine
AFT_FSDK_FaceFeatureDetect = internalLibrary.AFT_FSDK_FaceFeatureDetect
AFT_FSDK_GetVersion = internalLibrary.AFT_FSDK_GetVersion

AFT_FSDK_InitialFaceEngine.restype = c_long
AFT_FSDK_InitialFaceEngine.argtypes = (c_char_p,c_char_p,c_void_p,c_int32,POINTER(c_void_p),c_int32,c_int32,c_int32)
AFT_FSDK_UninitialFaceEngine.restype = c_long
AFT_FSDK_UninitialFaceEngine.argtypes = (c_void_p,)
AFT_FSDK_FaceFeatureDetect.restype = c_long
AFT_FSDK_FaceFeatureDetect.argtypes = (c_void_p,POINTER(ASVLOFFSCREEN),POINTER(POINTER(AFT_FSDK_FACERES)))
AFT_FSDK_GetVersion.restype = POINTER(AFT_FSDK_Version)
AFT_FSDK_GetVersion.argtypes =(c_void_p,)
