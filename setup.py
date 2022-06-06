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

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='qrplatba',
    version='0.5.0',
    packages=['qrplatba'],
    include_package_data=True,
    license='MPL',
    description='QR platba SVG QR code and SPAYD string generator',
    long_description=long_description,
    long_description_content_type='text/x-rst',
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
