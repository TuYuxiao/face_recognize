from .utils import trim, get_backend
import cv2
from .recognizer import FaceRecognizer


class FaceDetector:
    DEFAULT_INSTANCE = None

    def __init__(self, version='arcsoft_v3', num_face=30):
        self.backend = get_backend(version)
        self._detect_engine = None
        self._track_engine = None
        self._tracker = None
        self.num_face = num_face

        self.last_frame_infos = {}

    @classmethod
    def default(cls):
        if cls.DEFAULT_INSTANCE is None:
            cls.DEFAULT_INSTANCE = cls()
        return cls.DEFAULT_INSTANCE

    @property
    def detect_engine(self):
        if self._detect_engine:
            return self._detect_engine
        print("Init detect engine...")
        self._detect_engine = self.backend.init_engine(mode="image", num_face=self.num_face, mask='detect')
        return self._detect_engine

    @property
    def track_engine(self):
        if self._track_engine:
            return self._track_engine
        if self.backend.TRACK_ACCELERATE:
            print("Init track engine...")
            self._track_engine = self.backend.init_engine(mode="video", num_face=self.num_face, mask='detect')
        else:
            self._track_engine = self.detect_engine
        return self._track_engine

    @property
    def tracker(self):
        if self._tracker is None:
            self._tracker = DefaultTracker()
        return self._tracker

    def detect(self, img):
        img = trim(img)
        face_infos = self.backend.detect(self.detect_engine, img)
        return face_infos

    def extract(self, img, recognizer=None):
        img = trim(img)
        face_infos = self.backend.detect(self.detect_engine, img)
        if recognizer is None:
            recognizer = FaceRecognizer.default()
        features = []
        for info in face_infos:
            feature = recognizer.extract(img, info)
            if feature:
                features.append(feature)
        return features

    def detectFromPath(self, path):
        img = cv2.imread(path)
        return self.detect(img)

    def detectFromCoded(self, img):
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        return self.detect(img)

    def drawInfos(self, img, infos, show_name = True):
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fontText = ImageFont.truetype("font/simsun.ttc", 25, encoding="utf-8")
        for info in infos:
            draw.rectangle([(info.left, info.top), (info.right, info.bottom)], outline='red')
            if show_name:
                draw.text((info.left + 5, info.top + 5), info.name if info.name else "unknown", (255, 0, 0), font=fontText)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

    def track(self, img, tracker=None, recognizer=None):
        img = trim(img)
        face_infos = self.backend.track(self.track_engine, img)

        if not self.backend.TRACK_ID:
            if tracker is None:
                tracker = self.tracker
            tracker.track(face_infos)

        for info in face_infos:
            info.name = self.last_frame_infos.get(info.face_id)

        if recognizer is None:
            recognizer = FaceRecognizer.default()

        for info in face_infos:
            if info.name is None:
                feature = recognizer.extract(img, info)
                if feature is not None:
                    info.name = recognizer.recognize(feature)
                # TODO async recognize

        self.last_frame_infos = {info.face_id:info.name for info in face_infos if info.face_id is not None}

        return face_infos


class Tracker:
    def __init__(self):
        self.old_face_infos = []

    def track(self, new_face_infos):
        raise NotImplementedError()


class DefaultTracker(Tracker):
    def __init__(self):
        super().__init__()
        self.current_id = -1

    def assign_new_id(self):
        self.current_id += 1
        print("New face: %d" % self.current_id)
        return self.current_id

    def computeOverlapArea(self, leftA, bottomA, rightA, topA, leftB, bottomB, rightB, topB):
        if ((leftB >= rightA) or (topA >= bottomB) or (topB >= bottomA) or (leftA >= rightB)):
            return 0
        return (min(rightB, rightA) - max(leftA, leftB)) * (min(bottomA, bottomB) - max(topA, topB))

    def track(self, new_face_infos):
        for old_info in self.old_face_infos:
            maxOverlapArea = 0
            maxOverlapIndex = 0
            halfArea = ((old_info.bottom - old_info.top) * (old_info.right - old_info.left)) / 4
            for i, info in enumerate(new_face_infos):
                area = self.computeOverlapArea(info.left, info.bottom, info.right, info.top,
                                          old_info.left, old_info.bottom, old_info.right, old_info.top)

                if area > maxOverlapArea:
                    maxOverlapArea = area
                    maxOverlapIndex = i
            if maxOverlapArea > halfArea:
                new_face_infos[maxOverlapIndex].face_id = old_info.face_id
            else:
                print("Face %d is lost" % old_info.face_id)

        for info in new_face_infos:
            if info.face_id is None:
                info.face_id = self.assign_new_id()

        self.old_face_infos = new_face_infos
