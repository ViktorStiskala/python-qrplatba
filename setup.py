# coding=utf-8
import os
import sys
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

is_py_2_version = sys.version_info[0] == 2

requirements = ['qrcode>=3.0.0']

if is_py_2_version:
    requirements.append('six')


setup(
    name='qrplatba',
    version='0.3.4',
    packages=['qrplatba'],
    include_package_data=True,
    license='MPL',
    description='QR platba SVG QR code and SPAYD string generator',
    author='Viktor Stískala',
    author_email='viktor@stiskala.cz',
    install_requires=requirements,
    # test_suite='qrplatba.tests',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
