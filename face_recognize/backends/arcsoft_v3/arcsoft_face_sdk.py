import platform
import os
from ctypes import *
from face_recognize.common import ArcsoftFaceFeature

ASF_NONE = 0x00000000  # no feature
# tracking mode or detection mode
ASF_FACE_DETECT = 0x00000001
ASF_FACERECOGNITION = 0x00000004  # face feature
ASF_AGE = 0x00000008  # age
ASF_GENDER = 0x00000010  # gender
ASF_FACE3DANGLE = 0x00000020  # 3d angle
ASF_LIVENESS = 0x00000080  # RGB liveness
ASF_IR_LIVENESS = 0x00000400  # IR liveness

ASF_DETECT_MODE_VIDEO = 0x00000000  # Video mode
ASF_DETECT_MODE_IMAGE = 0xFFFFFFFF  # Image mode


class MPOINT(Structure):
    _fields_ = [('x', c_int32), ('y', c_int32)]


class MRECT(Structure):
    _fields_ = [('left', c_int32), ('top', c_int32), ('right', c_int32), ('bottom', c_int32)]


class ASF_VERSION(Structure):
    _fields_ = [('Version', c_char_p), ('BuildDate',
                                        c_char_p), ('CopyRight', c_char_p)]


ASF_OP_0_ONLY = 0x1  # 00...
ASF_OP_90_ONLY = 0x2  # 9090...
ASF_OP_270_ONLY = 0x3  # 270270...
ASF_OP_180_ONLY = 0x4  # 180180...
ASF_OP_ALL_OUT = 0x5  # 090270180090270180...
# VIDEO mode supports ASF_OP_0_HIGHER_EXT detection, IMAGE mode doesn't

ASF_OC_0 = 0x1  # 0 degree
ASF_OC_90 = 0x2  # 90 degree
ASF_OC_270 = 0x3  # 270 degree
ASF_OC_180 = 0x4  # 180 degree
ASF_OC_30 = 0x5  # 30 degree
ASF_OC_60 = 0x6  # 60 degree
ASF_OC_120 = 0x7  # 120 degree
ASF_OC_150 = 0x8  # 150 degree
ASF_OC_210 = 0x9  # 210 degree
ASF_OC_240 = 0xa  # 240 degree
ASF_OC_300 = 0xb  # 300 degree
ASF_OC_330 = 0xc  # 330 degree


class ASF_SingleFaceInfo(Structure):
    _fields_ = [('faceRect', MRECT), ('faceOrient', c_int32)]


class ASF_MultiFaceInfo(Structure):
    _fields_ = [('faceRect', POINTER(MRECT)), ('faceOrient', POINTER(c_int32)),
                ('faceNum', c_int32), ('faceID', POINTER(c_int32))]


class ASF_ActiveFileInfo(Structure):
    _fields_ = [('startTime', c_char_p), ('endTime', c_char_p), ('platform', c_char_p),
                ('sdkType', c_char_p), ('appId', c_char_p), ('sdkKey', c_char_p),
                ('sdkVersion', c_char_p), ('fileVersion', c_char_p)]


default_lib_path = os.path.expanduser("~/.face_recognize/lib")

if platform.system() == 'Windows':
    face_dll_path = os.path.join(default_lib_path, 'libarcsoft_face.dll')
    face_engine_dll_path = os.path.join(default_lib_path, 'libarcsoft_face_engine.dll')
else:
    face_dll_path = os.path.join(default_lib_path, 'libarcsoft_face.so')
    face_engine_dll_path = os.path.join(default_lib_path, 'libarcsoft_face_engine.so')

if (not os.path.exists(face_dll_path)) or (not os.path.exists(
    face_engine_dll_path)):
    print("Please download %s, %s from Arcsoft face recognition platform and move them to " \
                           "~/.face_recognize/lib " % (face_dll_path, face_engine_dll_path))
    exit()

face_dll = CDLL(face_dll_path)
face_engine_dll = CDLL(face_engine_dll_path)

ASFGetActiveFileInfo = face_engine_dll.ASFGetActiveFileInfo
ASFGetActiveFileInfo.restype = c_long
ASFGetActiveFileInfo.argtypes = (POINTER(ASF_MultiFaceInfo),)

ASFOnlineActivation = face_engine_dll.ASFOnlineActivation
ASFOnlineActivation.restype = c_long
ASFOnlineActivation.argtypes = (c_char_p, c_char_p)

ASFActivation = face_engine_dll.ASFActivation
ASFActivation.restype = c_long
ASFActivation.argtypes = (c_char_p, c_char_p)

ASFInitEngine = face_engine_dll.ASFInitEngine
ASFInitEngine.restype = c_long
ASFInitEngine.argtypes = (c_uint32, c_int32, c_int32,
                          c_int32, c_int32, POINTER(c_void_p))

ASFDetectFaces = face_engine_dll.ASFDetectFaces
ASFDetectFaces.restype = c_long
ASFDetectFaces.argtypes = (c_void_p, c_int32, c_int32, c_int32, POINTER(
    c_uint8), POINTER(ASF_MultiFaceInfo))


class ASF_LivenessThreshold(Structure):
    _fields_ = [('thresholdmodel_BGR', c_float),
                ('thresholdmodel_IR', c_float)]


ASFSetLivenessParam = face_engine_dll.ASFSetLivenessParam
ASFSetLivenessParam.restype = c_long
ASFSetLivenessParam.argtypes = (c_void_p, POINTER(ASF_LivenessThreshold))

ASFProcess = face_engine_dll.ASFProcess
ASFProcess.restype = c_long
ASFProcess.argtypes = (c_void_p, c_int32, c_int32, c_int32, POINTER(c_uint8),
                       POINTER(ASF_MultiFaceInfo), c_int32)

ASFProcess_IR = face_engine_dll.ASFProcess_IR
ASFProcess_IR.restype = c_long
ASFProcess_IR.argtypes = (c_void_p, c_int32, c_int32, c_int32, POINTER(c_uint8),
                          POINTER(ASF_MultiFaceInfo), c_int32)

ASFUninitEngine = face_engine_dll.ASFUninitEngine
ASFUninitEngine.restype = c_long
ASFUninitEngine.argtypes = (c_void_p,)

ASFGetVersion = face_engine_dll.ASFGetVersion
ASFGetVersion.restype = POINTER(ASF_VERSION)
ASFGetVersion.argtypes = (c_void_p,)


class ASF_FaceFeature(ArcsoftFaceFeature):
    _fields_ = [('feature', c_void_p), ('featureSize', c_int32)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _feature(self):
        return self.feature

    @_feature.setter
    def _feature(self, feature):
        self.feature = feature

    @property
    def feature_size(self):
        return self.featureSize

    @feature_size.setter
    def feature_size(self, feature_size):
        self.featureSize = feature_size


ASFFaceFeatureExtract = face_engine_dll.ASFFaceFeatureExtract
ASFFaceFeatureExtract.restype = c_long
ASFFaceFeatureExtract.argtypes = (c_void_p, c_int32, c_int32, c_int32, POINTER(
    c_uint8), POINTER(ASF_SingleFaceInfo), POINTER(ASF_FaceFeature))

ASFFaceFeatureCompare = face_engine_dll.ASFFaceFeatureCompare
ASFFaceFeatureCompare.restype = c_long
ASFFaceFeatureCompare.argtypes = (c_void_p, POINTER(
    ASF_FaceFeature), POINTER(ASF_FaceFeature), POINTER(c_float))


class ASF_AgeInfo(Structure):
    _fields_ = [('ageArray', POINTER(c_int32)), ('num', c_int32)]


ASFGetAge = face_engine_dll.ASFGetAge
ASFGetAge.restype = c_long
ASFGetAge.argtypes = (c_void_p, POINTER(ASF_AgeInfo))


class ASF_Face3DAngle(Structure):
    _fields_ = [('roll', POINTER(c_float)), ('yaw', POINTER(c_float)),
                ('pitch', POINTER(c_float)), ('status', POINTER(c_int32)), ('num', c_int32)]


ASFGetFace3DAngle = face_engine_dll.ASFGetFace3DAngle
ASFGetFace3DAngle.restype = c_long
ASFGetFace3DAngle.argtypes = (c_void_p, POINTER(ASF_Face3DAngle))


class ASF_LivenessInfo(Structure):
    _fields_ = [('isLive', POINTER(c_int32)), ('num', c_int32)]


ASFGetLivenessScore = face_engine_dll.ASFGetLivenessScore
ASFGetLivenessScore.restype = c_long
ASFGetLivenessScore.argtypes = (c_void_p, POINTER(ASF_LivenessInfo))

ASFGetLivenessScore_IR = face_engine_dll.ASFGetLivenessScore_IR
ASFGetLivenessScore_IR.restype = c_long
ASFGetLivenessScore_IR.argtypes = (c_void_p, POINTER(ASF_LivenessInfo))
