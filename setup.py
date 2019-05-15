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
    python3 -m pip freeze -r requirements-full-stable.txt > requirements-full-stable.txt

Upload to pypi:
	python3 -m twine upload dist/*

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

def get_list_from_file(*fullfilepath):
    return open(path.join(*fullfilepath), "r").read().splitlines()

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=app_version,
    description=('An application framework with built-in drivers (Controllers), '
                 'data holders (Sources) and config parsers (Rules). '
                 'Also includes a web interface for configuration and troubleshooting.'),
    long_description=long_description,
    url='https://bitbucket.org/fholmer/netdef',
    author='Frode Holmer',
    author_email='fholmer+netdef@gmail.com',
    license='GNU Lesser General Public License v3 or later',
    keywords='Application Framework Networking Monitoring',    

    python_requires='>=3.5',
    packages=find_packages(include=['netdef*']),

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=get_list_from_file(here, "docs", "classifiers.txt"),

    install_requires=get_list_from_file(here, "requirements-minimal.txt"),

    extras_require={
        'full':get_list_from_file(here, "requirements-full.txt"),
        'full-stable':get_list_from_file(here, "requirements-full-stable.txt"),
    },

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
