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
`pip install dlib`  
`pip install face_recognition_models`
##### Enable arcsoft_v1
Download ArcSoft Face Recognition SDK 1.0 from [ArcSoft](https://ai.arcsoft.com.cn/product/arcface.html).  
Move libarcsoft_fsdk_face_detection.dll(.so), libarcsoft_fsdk_face_recognition.dll(.so), libarcsoft_fsdk_face_tracking.dll(.so)
to $HOME/.face_recognize/lib.  
Modify $HOME/.face_recognize/config/arcsoft_v1_config.py and set the APPID, KEY.

