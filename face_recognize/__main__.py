from . import FaceDetector, FaceRecognizer
import cv2

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", metavar="<command>", help="'recognize' or 'register' or 'delete' or 'clear' or 'init'")
    parser.add_argument('--version', default="arcsoft_v3", choices=["arcsoft_v1", "arcsoft_v3", "dlib"],
                        metavar="recognizer version", help='Recognizer Version')
    parser.add_argument('--name', metavar="user name", help='user name')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('--image', metavar="path to image",
                       help='Image to recognize or register')
    group.add_argument('--video', metavar="path to image",
                       help='Video to recognize')

    args = parser.parse_args()

    if args.command == 'recognize':
        recognizer = FaceRecognizer(version=args.version)
        recognizer.load_feature_from_db()
        detector = FaceDetector(version=args.version)

        if args.image:
            img = cv2.imread(args.image)
            assert img is not None, "Fail to open image"
            infos = detector.detect(img)
            infos.sort(key=lambda x: (x.left + x.right) / 2)

            names = []
            for info in infos:
                feature = recognizer.extract(img, info)
                name = recognizer.recognize(feature)
                names.append(name if name else "unknown")

            print("People names in image (from left to right): ", ', '.join(names))
        else:
            video = args.video
            try:
                video = int(video)
            except ValueError as e:
                pass

            cap = cv2.VideoCapture(video)
            while True:
                ret, img = cap.read()
                if (not ret) or cv2.waitKey(1) in [ord('q'), 27]:
                    break
                face_infos = detector.track(img, recognizer=recognizer)
                img = detector.drawInfos(img, face_infos)
                cv2.imshow('face recognize', img)

    elif args.command == 'register':
        import os
        assert args.image is not None
        detector = FaceDetector(version=args.version)
        recognizer = FaceRecognizer(version=args.version)

        if os.path.isdir(args.image):
            import glob
            images = glob.glob(os.path.join(args.image, "*[.jpg,.jpeg,.png,.bmp,.JPG,.JPEG,.PNG,.BMP]"))
            recognizer.register_feature(images, detector=detector)
        else:
            if args.name:
                recognizer.register_feature([args.image], names=[args.name], detector=detector)
            else:
                recognizer.register_feature([args.image], detector=detector)

    elif args.command == 'delete':
        assert args.name is not None
        from .database import delete_user
        delete_user(args.name)

    elif args.command == 'clear':
        from .database import drop_all
        drop_all()

    elif args.command == 'init':
        import os
        default_lib_path = os.path.expanduser("~/.face_recognize/config")
        if not os.path.exists(default_lib_path):
            os.makedirs(default_lib_path)

        default_config_path = os.path.expanduser("~/.face_recognize/config")
        if not os.path.exists(default_config_path):
            os.makedirs(default_config_path)

        arcsoft_v3_config_file_path = os.path.join(default_config_path, "arcsoft_v3_config.py")
        if not os.path.exists(arcsoft_v3_config_file_path):
            config_file_template = \
                """
                import platform
                from ctypes import c_char_p
                APPID = b""
                if platform.system() == 'Windows':
                    SDKKEY = b""
                else:
                    SDKKEY = b""
                """
            with open(arcsoft_v3_config_file_path, 'w') as f:
                f.write(config_file_template)
            print("Config file generated: %s, please modify APPID and KEY" % arcsoft_v3_config_file_path)

        arcsoft_v1_config_file_path = os.path.join(default_config_path, "arcsoft_v1_config.py")
        if not os.path.exists(arcsoft_v1_config_file_path):
            config_file_template = \
                """
                import platform
                from ctypes import c_char_p
                APPID = c_char_p(b'')
                if platform.system() == 'Windows':
                    FD_SDKKEY = c_char_p(b'')
                    FT_SDKKEY = c_char_p(b'')
                    FR_SDKKEY = c_char_p(b'')
                else:
                    FD_SDKKEY = c_char_p(b'')
                    FT_SDKKEY = c_char_p(b'')
                    FR_SDKKEY = c_char_p(b'')
                """
            with open(arcsoft_v1_config_file_path, 'w') as f:
                f.write(config_file_template)
            print("Config file generated: %s, please modify APPID and KEY" % arcsoft_v1_config_file_path)

    else:
        print("Invalid command!!!")


if __name__ == '__main__':
    main()