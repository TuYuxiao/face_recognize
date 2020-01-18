from .utils import trim
import cv2
from . import get_backend


class FaceDetector:
    def __init__(self, num_face=30, mode='image', version='arcsoft_v3'):
        self.mode = mode
        self.backend = get_backend(version)
        self.engine = self.backend.init_engine(mode=self.mode, num_face=num_face, mask='detect')
        self.last_frame_infos = {}

    def detect(self, img):
        img = trim(img)
        face_infos = self.backend.detect(self.engine, img, mode=self.mode)
        return face_infos

    def detectFromPath(self, path):
        img = cv2.imread(path)
        return self.detect(img)

    def detectFromCoded(self, img):
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        return self.detect(img)

    def drawInfos(self, img, infos):
        for info in infos:
            cv2.rectangle(img, (info.left, info.top), (info.right, info.bottom), (0, 0, 255), 2)
            cv2.putText(img, str(info.name), (info.left + 5, info.top + 25), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255),
                        2)
        return img

    def track(self, face_infos):
        this_frame_infos = {}
        for info in face_infos:
            if self.last_frame_infos.get(str(info.face_id)):
                info.name = self.last_frame_infos.get(str(info.face_id))
                print(info.name)
            this_frame_infos[str(info.face_id)] = info.name
        self.last_frame_infos = this_frame_infos
        return face_infos
