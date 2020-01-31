from .utils import trim, get_backend
from .common import FaceInfo
from collections import defaultdict
import cv2
import os
import numpy as np


class FaceRecognizer:
    DEFAULT_INSTANCE = None

    def __init__(self, version='arcsoft_v3'):
        self.version = version
        self.backend = get_backend(version)
        self.engine = self.backend.init_engine(mask='recognize')
        self.features = defaultdict(list)
        self.THRESHOLD = self.backend.THRESHOLD

        self._register_names = []
        self._register_features = []

    @classmethod
    def default(cls):
        if cls.DEFAULT_INSTANCE is None:
            cls.DEFAULT_INSTANCE = cls()
            cls.DEFAULT_INSTANCE.load_feature_from_db()
        return cls.DEFAULT_INSTANCE

    def load_feature_from_db(self):
        from .database import Session, UserFeature, User
        self.clear_feature()
        sess = Session()
        for u, f in sess.query(User, UserFeature).filter(User.id == UserFeature.user_id).filter(
                UserFeature.feature_version == self.version).all():
            self._add_feature(u.name, self.backend.FaceFeature.fromByteArray(f.user_feature))
        sess.close()

    def register_feature(self, images, names=None, *, to_db=True, to_buffer=False, detector=None):
        """
        if names is None, images should be paths of images.
        """
        if names is None:
            names = [os.path.basename(i).split('.')[0] for i in images]
        if detector is None:
            from .detector import FaceDetector
            detector = FaceDetector.default()

        for name, img in zip(names, images):
            if isinstance(img, str):
                img = cv2.imdecode(np.fromfile(img, dtype=np.uint8), cv2.IMREAD_COLOR)
            if not isinstance(img, np.ndarray):
                print("Invalid image for user %s" % name)
                continue

            if to_db:
                self._add_register_feature(name, img, detector)
            if to_buffer:
                self.add_feature(name, img, detector)

        if to_db:
            self.commit()

    def commit(self):
        from .database import save_feature
        save_feature(self._register_names, self._register_features, self.version)
        self._register_names.clear()
        self._register_features.clear()

    def _add_register_feature(self, name, img, detector):
        infos = detector.detect(img)
        if len(infos) != 1:
            print("Image contains %d people, don't support!!!" % len(infos))
            return
        feature = self.extract(img, infos[0])
        if feature is None:
            print("Fail to extract face feature!!!")
            return

        self._register_names.append(name)
        self._register_features.append(feature)

    def add_feature(self, name, img, detector):
        infos = detector.detect(img)
        if len(infos) != 1:
            print("Image contains %d people, don't support!!!" % len(infos))
            return
        feature = self.extract(img, infos[0])
        if feature is None:
            print("Fail to extract face feature!!!")
            return

        self._add_feature(name, feature)

    def _add_feature(self, name, feature):
        self.features[name].append(feature)

    def clear_feature(self):
        self.features.clear()

    def extract(self, img, face_info=None):
        img = trim(img)
        if not face_info:
            face_info = FaceInfo(0x1, 0, 0, img.shape[1], img.shape[0])
        return self.backend.extract(self.engine, img, face_info)

    def compare(self, feature1, feature2):
        return self.backend.compare(self.engine, feature1, feature2)

    def judge(self, feature1, feature2):
        return self.compare(feature1, feature2) > self.THRESHOLD

    def recognize(self, feature, early_stop=False):
        max_score, max_name = 0., None
        for name, user_features in self.features.items():
            score = max(self.compare(feature, f) for f in user_features)
            if score > max_score:
                max_score = score
                max_name = name
                if early_stop and max_score > self.THRESHOLD:
                    break
        print("Recognize Result:", max_score, max_name)
        if max_score < self.THRESHOLD:
            return
        return max_name
