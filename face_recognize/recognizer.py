from .utils import trim
from .common import FaceInfo
from . import get_backend


class FaceRecognizer:
    def __init__(self, version='arcsoft_v3'):
        self.backend = get_backend(version)
        self.engine = self.backend.init_engine(mask='recognize')
        self.features = {}
        self.THRESH = 0.8

    def extract(self, img, face_info=None):
        img = trim(img)
        if not face_info:
            face_info = FaceInfo(0x1, 0, 0, img.shape[1], img.shape[0])
        return self.backend.extract(self.engine, img, face_info)

    def compare(self, feature1, feature2):
        return self.backend.compare(self.engine, feature1, feature2)

    def recognize(self, feature, early_stop=True):
        max_score, max_name = 0., 'unknown'
        for name, f in self.features.items():
            score = self.compare(feature, f)
            if score > max_score:
                max_score = score
                max_name = name
                if early_stop and max_score > self.THRESH:
                    break
        return max_score, max_name
