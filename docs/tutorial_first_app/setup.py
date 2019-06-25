from setuptools import setup, find_packages
from first_app import __version__ as app_version

NAME = "First-App"
MAIN_PACKAGE = "first_app"

setup(
    name=NAME,
    version=app_version,
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'config']),    
    install_requires=[
        'netdef'
    ],
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
