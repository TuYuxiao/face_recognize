from .detector import FaceDetector
from .recognizer import FaceRecognizer
import os

default_lib_path = os.path.expanduser("~/.face_recognize/lib")
if not os.path.exists(default_lib_path):
    os.makedirs(default_lib_path)
