# face_recognize

Build face recognition application easily.
This library provides a simple way to use [dlib](http://dlib.net/)'s 
state-of-the-art face recognition and [ArcSoft](https://ai.arcsoft.com.cn/product/arcface.html)'s free offline 
face recognition SDK (which is quicker and more robust than dlib model).

## Installation
`pip install face_recognize`

#### Installation Options:
This library supports three backends for now:
* arcsoft_v1: ArcSoft Face Recognition SDK 1.0
* arcsoft_v3: ArcSoft Face Recognition SDK 2.0/3.0
* dlib
##### Enable dlib backend
* `pip install dlib`  
* `pip install face_recognition_models`
##### Enable arcsoft_v1
* Download ArcSoft Face Recognition SDK 1.0 from [ArcSoft](https://ai.arcsoft.com.cn/product/arcface.html).  
* `face_recognize init`
* Move libarcsoft_fsdk_face_detection.dll(.so), libarcsoft_fsdk_face_recognition.dll(.so), libarcsoft_fsdk_face_tracking.dll(.so)
to $HOME/.face_recognize/lib.  
* Modify $HOME/.face_recognize/config/arcsoft_v1_config.py and set the APPID, KEY.
##### Enable arcsoft_v3
* Download ArcSoft Face Recognition SDK 3.0 from [ArcSoft](https://ai.arcsoft.com.cn/product/arcface.html).  
* `face_recognize init`
* Move libarcsoft_face.dll(.so), libarcsoft_face_engine.dll(.so)
to $HOME/.face_recognize/lib.  
* Modify $HOME/.face_recognize/config/arcsoft_v3_config.py and set the APPID, KEY.

## Usage
### CLI
#### Register user with image
`face_recognize register --image path-to-image (--name user-name)`  
#### Recognize people in an image
`face_recognize recognize --image path-to-image`
#### Recognize people in a video
`face_recognize recognize --video path-to-video`  
#### Recognize people in usb camera
`face_recognize recognize --video 0`  

The backend is default to be arcsoft_v3, use `--verion backend-verson` to indicate the backend.

### Python Module

#### Face Detection
```
from face_recognize import FaceDetector
import cv2
img = cv2.imread('sample.jpg')
detector = FaceDetector()
infos = detector.detect(img)
detector.drawInfos(img, infos, show_name=False)
cv2.imshow('img', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

```

#### Face Feature Extraction
```
from face_recognize import FaceDetector, FaceRecognizer
import cv2
img = cv2.imread('sample.jpg')
detector = FaceDetector()
recognizer = FaceRecognizer()
infos = detector.detect(img)
feature = recognizer.extract(img, infos[0])
```

#### Face Feature Compare
```
from face_recognize import FaceDetector, FaceRecognizer
import cv2
img1 = cv2.imread('me.jpg')
img2 = cv2.imread('unknown.jpg')
detector = FaceDetector()
recognizer = FaceRecognizer()
infos1 = detector.detect(img1)
infos2 = detector.detect(img2)
feature1 = recognizer.extract(img1, infos1[0])
feature2 = recognizer.extract(img2, infos2[0])

if recognizer.judge(feature1, feature2):
    print("This is me")
else:
    print("This is not me")
```

#### Face Recognition (without db)
```
from face_recognize import FaceDetector, FaceRecognizer
import cv2

detector = FaceDetector()
recognizer = FaceRecognizer()
recognizer.register_feature(['me.jpg'], name=['me'], to_db=False, to_buffer=True, detector=detector)

img = cv2.imread('unknown.jpg')
infos = detector.detect(img)
feature = recognizer.extract(img, infos[0])
name = recognizer.recognize(feature)
if name:
    print("This is %s" % name)
else:
    print("Unknown")
```


#### Recognize People in Usb Camera (with db)
```
from face_recognize import FaceDetector
from cv2_utils import VideoCapture

detector = FaceDetector()

cap = VideoCapture(0, show_video=True, show_fps=True)
for img in cap:
    face_infos = detector.track(img)
    detector.drawInfos(img, face_infos)
```