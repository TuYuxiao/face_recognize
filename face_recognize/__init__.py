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
