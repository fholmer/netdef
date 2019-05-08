#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html


To build sdist:
    python3 setup.py sdist

To build wheel:
    install wheel:
      python3 -m pip install wheel
    build wheel:
      python3 setup.py bdist_wheel

Update requirements:
    python3 -m pip freeze -r requirements-stable.txt > requirements-stable.txt

Download required packages:
    
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from netdef import __version__ as app_version

here = path.abspath(path.dirname(__file__))

NAME = 'netdef'
MAIN_PACKAGE = 'netdef'

setup(
    name=NAME,
    version=app_version,
    description=NAME,
    #long_description=long_description,
    url='',

    # Author details
    author='Frode Holmer',
    author_email='fholmer+netdef@gmail.com',

    # Choose your license
    license='LGPL',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Monitoring',
        'License :: LGPL',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows'
    ],
    keywords='Networking Monitoring',    
    packages=find_packages(include=['netdef*']),
    install_requires=[
        'aiohttp',
        'beautifulsoup4',
        'crontab',
        'cryptography',
        'Flask',
        'Flask-Admin',
        'Flask-BasicAuth',
        'Flask-Login',
        'freeopcua',
        'pika',
        'psutil',
        'pymodbus',
        'Werkzeug'
    ],
    python_requires='>=3.5',
    package_data={
        MAIN_PACKAGE: [
            'Engines/templates/*.html',
            'Engines/templates/*/*.html'
        ]
    },    
    entry_points={
        'console_scripts': [
            '{NAME}={MAIN_PACKAGE}.__main__:cli'.format(NAME=NAME, MAIN_PACKAGE=MAIN_PACKAGE),
        ],
    },
)
