from face_recognize.common import FaceFeature
import numpy as np

class DlibFaceFeature(FaceFeature):
    def __init__(self, feature, **kwargs):
        super().__init__()
        self.feature = feature

    @classmethod
    def fromByteArray(cls, byteArrayFeature):
        return cls(np.fromstring(byteArrayFeature, dtype=np.float64))

    def toByteArray(self):
        return self.feature.tobytes()