from . import FaceDetector, FaceRecognizer
import cv2

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", metavar="<command>", help="'recognize' or 'register'")
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
        assert args.image is not None
        img = cv2.imread(args.image)
        assert img is not None, "Fail to open image"
        detector = FaceDetector(version=args.version)
        recognizer = FaceRecognizer(version=args.version)
        if args.name:
            recognizer.register_feature([args.image], names=[args.name], detector=detector)
        else:
            recognizer.register_feature([args.image], detector=detector)

    else:
        print("Invalid command!!!")
