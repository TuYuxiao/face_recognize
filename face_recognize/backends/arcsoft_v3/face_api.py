from .asvloffscreen import ASVL_PAF_RGB24_B8G8R8
from .arcsoft_face_sdk import *
from .merror import MOK, MERR_ASF_ALREADY_ACTIVATED
from face_recognize.common import FaceInfo
from ctypes import *

import platform

APPID = b"AANTqgLuerZzjWdvtAJyx8p589erGMQX5x39C1urYbne"
if platform.system() == 'Windows':
    SDKKEY = b"Co5UzVAgjkQD3skZwEQHxRRjCXv1krzBBo3RxL3ha351"
else:
    SDKKEY = b"Co5UzVAgjkQD3skZwEQHxRRj4RLum5hcU5fDATRmSbpG"

MASK = {'all': (
        ASF_FACE_DETECT | ASF_FACERECOGNITION | ASF_AGE | ASF_GENDER | ASF_FACE3DANGLE | ASF_LIVENESS | ASF_IR_LIVENESS),
    'detect': ASF_FACE_DETECT, 'recognize': ASF_FACERECOGNITION, 'detect_live': ASF_FACE_DETECT | ASF_LIVENESS,
    'age': ASF_AGE, 'gender': ASF_GENDER, 'face_angle': ASF_FACE3DANGLE,
    'detect_recognize': (ASF_FACE_DETECT | ASF_FACERECOGNITION)}


def activation():
    res = ASFOnlineActivation(APPID, SDKKEY)
    if res != MOK and res != MERR_ASF_ALREADY_ACTIVATED:
        print("ASFOnlineActivation fail: %d" % res)
        return False
    else:
        print("ASFOnlineActivation sucess: %d" % res)
        return True


def init_engine(mode='image', num_face=10, mask='all'):
    handle = c_void_p()
    priority = ASF_OP_ALL_OUT if mode == 'image' else ASF_OP_ALL_OUT
    n_scale = 32 if mode == 'image' else 16
    mode = ASF_DETECT_MODE_IMAGE if mode == 'image' else ASF_DETECT_MODE_VIDEO
    mask = MASK[mask]
    res = ASFInitEngine(mode, priority, n_scale, num_face, mask, byref(handle))
    if res != MOK:
        print("ALInitEngine fail: %d" % res)
        return None
    else:
        print("ALInitEngine sucess: %d" % res)
        return handle


def detect(engine, img, mode='image'):
    assert img.shape[1] % 4 == 0
    assert img.shape[0] % 2 == 0
    face_info = ASF_MultiFaceInfo()
    res = ASFDetectFaces(engine, img.shape[1], img.shape[0], ASVL_PAF_RGB24_B8G8R8,
                         img.ctypes.data_as(POINTER(c_ubyte)),
                         byref(face_info))  # cast(bytes(img.data), POINTER(c_uint8))

    if res != MOK:
        print("ASFDetectFaces fail: %d" % res)
        return None

    face_infos = []
    for i in range(face_info.faceNum):
        face_id = None if mode == 'image' else face_info.faceID[i]
        rect = face_info.faceRect[i]
        face_infos.append(FaceInfo(face_info.faceOrient[i], max(rect.left, 0),
                                   max(rect.top, 0), min(rect.right, img.shape[1]), min(rect.bottom, img.shape[0]),
                                   face_id))
        # face_infos.append(cls(face_info.faceOrient[i],rect.left,
        #        rect.top,rect.right,rect.bottom,face_id))
    return face_infos


def to_asf(face_info):
    fi = ASF_SingleFaceInfo()
    fi.faceRect.left = face_info.left
    fi.faceRect.top = face_info.top
    fi.faceRect.right = face_info.right
    fi.faceRect.bottom = face_info.bottom
    fi.faceOrient = face_info.orient
    return fi


def extract(engine, img, face_info):
    assert img.shape[1] % 4 == 0
    assert img.shape[0] % 2 == 0
    face_info = to_asf(face_info)
    face_feature = ASF_FaceFeature()
    res = ASFFaceFeatureExtract(engine, img.shape[1], img.shape[0], ASVL_PAF_RGB24_B8G8R8,
                                img.ctypes.data_as(POINTER(c_ubyte)), face_info, byref(face_feature))
    if res != MOK:
        print("ASFFaceFeatureExtract fail: %d" % res)
        return None
    return face_feature.copy()


def compare(engine, feature1, feature2):
    score = c_float(0.0)
    res = ASFFaceFeatureCompare(engine, byref(feature1), byref(feature2), byref(score))
    if res != MOK:
        print("ASFFaceFeatureCompare fail: %d" % res)
        return 0.
    return score.value
