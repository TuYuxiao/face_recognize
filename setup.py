from setuptools import setup, find_packages
import platform

if platform.system() == 'Windows':
    package_data = {'': ['*.dll', '*.lib']}
else:
    package_data = {'': ['*.so']}

setup(
    name = 'face_recognize',
    version = '0.1.0',
    description = 'face recognize with dlib and arcsoft toolkit',
    license = 'MIT License',
    author = 'Tu Yuxiao',
    author_email = '754738085@qq.com',
    url = 'https://github.com/TuYuxiao/face_recognize',
    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires = ['opencv-python'],
    keywords = ['face recognize'],
    package_data = package_data,
)