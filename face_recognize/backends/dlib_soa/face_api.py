import dlib
import face_recognition_models
import numpy as np
from face_recognize.common import FaceInfo
from . import DlibFaceFeature

THRESHOLD = 0.4
TRACK_ACCELERATE = False
TRACK_ID = False

FaceFeature = DlibFaceFeature


def to_rect(face_info):
    return dlib.rectangle(face_info.left, face_info.top, face_info.right, face_info.bottom)


def init_engine(mode='image', num_face=10, mask='all'):
    if mask == 'recognize':
        predictor_5_point_model = face_recognition_models.pose_predictor_five_point_model_location()
        pose_predictor_5_point = dlib.shape_predictor(predictor_5_point_model)
        #predictor_68_point_model = face_recognition_models.pose_predictor_model_location()
        #pose_predictor_68_point = dlib.shape_predictor(predictor_68_point_model)
        face_recognition_model = face_recognition_models.face_recognition_model_location()
        face_encoder = dlib.face_recognition_model_v1(face_recognition_model)
        return pose_predictor_5_point, face_encoder
    else:
        face_detector = dlib.get_frontal_face_detector()
        return face_detector
        #cnn_face_detection_model = face_recognition_models.cnn_face_detector_model_location()
        #cnn_face_detector = dlib.cnn_face_detection_model_v1(cnn_face_detection_model)
        #return cnn_face_detector


def detect(engine, img, number_of_times_to_upsample=1):
    img = img[..., ::-1]
    locations = engine(img,number_of_times_to_upsample)
    face_infos = []
    for rect in locations:
        if isinstance(engine, dlib.cnn_face_detection_model_v1):
            rect = rect.rect
        face_infos.append(FaceInfo(0, max(rect.left(), 0),
                                   max(rect.top(), 0), min(rect.right(), img.shape[1]),
                                   min(rect.bottom(), img.shape[0]), 0))
    return face_infos


def track(engine, img, number_of_times_to_upsample=1):
    return detect(engine, img, number_of_times_to_upsample)


def extract(engine, img, face_info, *, num_jitters=1):
    pose_predictor, face_encoder = engine

    img = img[..., ::-1]
    landmark = pose_predictor(img, to_rect(face_info))

    return DlibFaceFeature(np.array(face_encoder.compute_face_descriptor(img, landmark, num_jitters)))


def compare(engine, feature1, feature2):
    return 1. - np.linalg.norm(feature1.feature - feature2.feature)
