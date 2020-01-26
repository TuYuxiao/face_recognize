from . import FaceDetector, FaceRecognizer
import cv2

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", metavar="<command>", help="'recognize' or 'register'")
    parser.add_argument('--image', required=True, metavar="path to image",
                        help='Image to recognize or register')
    parser.add_argument('--version', default="arcsoft_v3", choices=["arcsoft_v1", "arcsoft_v3", "dlib"],
                        metavar="recognizer version", help='Recognizer Version')

    args = parser.parse_args()

    img = cv2.imread(args.image)
    assert img is not None, "Fail to open image"

    if args.command == 'recognize':
        recognizer = FaceRecognizer(version=args.version)
        detector = FaceDetector()

        infos = detector.detect(img)
        infos.sort(key=lambda x: (x.left+x.right)/2)

        names = []
        for info in infos:
            feature = recognizer.extract(img, info)
            name = recognizer.recognize(feature)
            names.append(name if name else "unknown")

        print("People names in image: ", ', '.join(names))
        
    elif args.command == 'register':
        recognizer = FaceRecognizer(version=args.version)
        recognizer.register_feature([args.image])

    else:
        print("Invalid command!!!")
