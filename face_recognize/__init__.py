BACKEND = {'arcsoft_v1': None, 'arcsoft_v3': None}


def get_backend(version):
    if BACKEND.get(version):
        return BACKEND.get(version)
    if version == 'arcsoft_v1':
        from .backends.arcsoft_v1 import face_api
    elif version == 'arcsoft_v3':
        from .backends.arcsoft_v3 import face_api
    else:
        face_api = None
    BACKEND[version] = face_api
    return BACKEND.get(version)
