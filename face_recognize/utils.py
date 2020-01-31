BACKEND = {'arcsoft_v1': None, 'arcsoft_v3': None, 'dlib': None}


def get_backend(version):
    if BACKEND.get(version):
        return BACKEND.get(version)
    if version == 'arcsoft_v1':
        from .backends.arcsoft_v1 import face_api
    elif version == 'arcsoft_v3':
        from .backends.arcsoft_v3 import face_api
    elif version == 'dlib':
        from .backends.dlib_soa import face_api
    else:
        assert False, "Backend doesn't exists!!!"
    BACKEND[version] = face_api
    return BACKEND.get(version)


def trim(img):
    height, width = img.shape[0], img.shape[1]
    clip_w = width % 4
    clip_h = height % 2
    if clip_w == 0 and clip_h == 0:
        return img
    return img[:height - clip_h, :width - clip_w, :].copy()
