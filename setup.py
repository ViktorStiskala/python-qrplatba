# coding=utf-8
import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='qrplatba',
	version='0.3.2',
	packages=['qrplatba'],
	include_package_data=True,
	license='MPL',
	description='QR platba SVG QR code and SPAYD string generator',
	author='Viktor Stískala',
	author_email='viktor@stiskala.cz',
	install_requires=[
		'qrcode>=3.0.0',
	],
	# test_suite='qrplatba.tests',
	classifiers=[
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.3',
		'Topic :: Software Development :: Libraries',
		'Topic :: Software Development :: Python Modules',
	],
)
