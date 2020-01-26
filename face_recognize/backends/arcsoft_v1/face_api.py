from . import ASVL_COLOR_FORMAT

from .AFT_FSDKLibrary import *
from .AFR_FSDKLibrary import *
from .AFD_FSDKLibrary import *
from . import ASVLOFFSCREEN
from face_recognize.common import FaceInfo, malloc, free
from ctypes import *
import sys


THRESHOLD = 0.58
TRACK_ACCELERATE = True
TRACK_ID = False

FaceFeature = AFR_FSDK_FACEMODEL

default_config_path = os.path.expanduser("~/.face_recognize/config")
if not os.path.exists(default_config_path):
    os.makedirs(default_config_path)
config_file_path = os.path.join(default_config_path, "arcsoft_v1_config.py")
if os.path.exists(config_file_path):
    sys.path.append(default_config_path)
    from arcsoft_v1_config import APPID, FD_SDKKEY, FT_SDKKEY, FR_SDKKEY
else:
    config_file_template = \
"""
import platform
from ctypes import c_char_p
APPID = c_char_p(b'')
if platform.system() == 'Windows':
    FD_SDKKEY = c_char_p(b'')
    FT_SDKKEY = c_char_p(b'')
    FR_SDKKEY = c_char_p(b'')
else:
    FD_SDKKEY = c_char_p(b'')
    FT_SDKKEY = c_char_p(b'')
    FR_SDKKEY = c_char_p(b'')
"""
    with open(config_file_path, 'w') as f:
        f.write(config_file_template)

    print("Please edit config file: %s and setup keys" % config_file_path)
    exit()




def getImg(frame):
    '''
    Convert Mat object to ASVLOFFSCREEN object
    '''
    inputImg = ASVLOFFSCREEN()
    inputImg.u32PixelArrayFormat = ASVL_COLOR_FORMAT.ASVL_PAF_RGB24_B8G8R8
    inputImg.i32Width = frame.shape[1]
    inputImg.i32Height = frame.shape[0]
    inputImg.pi32Pitch[0] = frame.shape[1]*3
    inputImg.ppu8Plane[0] = frame.ctypes.data_as(POINTER(c_ubyte))
    inputImg.ppu8Plane[1] = cast(0, POINTER(c_ubyte))
    inputImg.ppu8Plane[2] = cast(0, POINTER(c_ubyte))
    inputImg.ppu8Plane[3] = cast(0, POINTER(c_ubyte))
    inputImg.gc_ppu8Plane0 = bytes(frame.data)
    return inputImg

def init_engine(mode='image',num_face=10,mask='all'):
    engine = c_void_p()
    if mask == 'recognize':
        WORKBUF_SIZE = 40 * 1024 * 1024
        workMem = malloc(c_size_t(WORKBUF_SIZE))
        ret = AFR_FSDK_InitialEngine(APPID, FR_SDKKEY,
                workMem, c_int32(WORKBUF_SIZE),
                byref(engine))
    else:
        WORKBUF_SIZE = 20 * 1024 * 1024
        workMem = malloc(c_size_t(WORKBUF_SIZE))
        if mode == 'image':
            ret = AFD_FSDK_InitialFaceEngine(APPID, FD_SDKKEY,
                    workMem, c_int32(WORKBUF_SIZE),
                    byref(engine), AFD_FSDK_OPF_0_HIGHER_EXT, 16, num_face)
        elif mode == 'video':
            ret = AFT_FSDK_InitialFaceEngine(APPID, FT_SDKKEY,
                    workMem, c_int32(WORKBUF_SIZE),
                    byref(engine), AFT_FSDK_OPF_0_HIGHER_EXT, 16, num_face)
        else:
            assert False, "invalid engine mode"

    if ret != 0:
        free(workMem)
        print('Initial %s engine fail: %s, %s \nPlease check SDK keys'%(mode, mask, ret))
        exit()

    return engine

def detect(engine, img):
    inputImg = getImg(img)
    faceInfo = []

    pFaceRes = POINTER(AFD_FSDK_FACERES)()
    ret = AFD_FSDK_StillImageFaceDetection(engine, byref(inputImg), byref(pFaceRes))

    if ret != 0:
        print('FSDK_FaceFeatureDetect 0x{0:x}'.format(ret))
        return faceInfo

    faceRes = pFaceRes.contents
    if faceRes.nFace > 0:
        for i in range(0, faceRes.nFace):
            rect = faceRes.rcFace[i]
            orient = faceRes.lfaceOrient.contents
            faceInfo.append(FaceInfo(orient,rect.left,rect.top,rect.right,rect.bottom))
    return faceInfo

def track(engine, img):
    inputImg = getImg(img)
    faceInfo = []

    pFaceRes = POINTER(AFT_FSDK_FACERES)()
    ret = AFT_FSDK_FaceFeatureDetect(engine, byref(inputImg), byref(pFaceRes))

    if ret != 0:
        print('FSDK_FaceFeatureDetect 0x{0:x}'.format(ret))
        return faceInfo

    faceRes = pFaceRes.contents
    if faceRes.nFace > 0:
        for i in range(0, faceRes.nFace):
            rect = faceRes.rcFace[i]
            orient = faceRes.lfaceOrient
            faceInfo.append(FaceInfo(orient,rect.left,rect.top,rect.right,rect.bottom))
    return faceInfo

def extract(engine, img, face_info):
    img = getImg(img)

    faceinput = AFR_FSDK_FACEINPUT()
    faceinput.lOrient = face_info.orient
    faceinput.rcFace.left = face_info.left
    faceinput.rcFace.top = face_info.top
    faceinput.rcFace.right = face_info.right
    faceinput.rcFace.bottom = face_info.bottom

    faceFeature = AFR_FSDK_FACEMODEL()
    ret = AFR_FSDK_ExtractFRFeature(engine, img, faceinput, faceFeature)
    if ret != 0:
        print('AFR_FSDK_ExtractFRFeature ret 0x{0:x}'.format(ret))
        return None

    try:
        return faceFeature.copy()
    except Exception as e:
        print(e.message)
        return None

def compare(engine, feature1, feature2):
    #feature1 = AFR_FSDK_FACEMODEL.fromByteArray(feature1)
    #feature2 = AFR_FSDK_FACEMODEL.fromByteArray(feature2)

    fSimilScore = c_float(0.0)
    ret = AFR_FSDK_FacePairMatching(engine, feature1, feature2, byref(fSimilScore))
    if ret != 0:
        print('AFR_FSDK_FacePairMatching failed:ret 0x{0:x}'.format(ret))
        return 0.0
    return fSimilScore.value
