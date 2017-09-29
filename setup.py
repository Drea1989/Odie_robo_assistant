#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re
import sys
from setuptools import setup, find_packages
from codecs import open
from os import path

basedir = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


# locate our version number
def read_version_py(file_name):
    try:
        version_string_line = open(file_name, "rt").read()
    except EnvironmentError:
        return None
    else:
        version_regex = r"^version_str = ['\"]([^'\"]*)['\"]"
        mo = re.search(version_regex, version_string_line, re.M)
        if mo:
            return mo.group(1)

VERSION_PY_FILENAME = 'odie/_version.py'
version = read_version_py(VERSION_PY_FILENAME)

py2_prefix = ''
if sys.version_info[0] < 3:
    py2_prefix = 'python2-'

setup(
    name='odie',
    version=version,
    description='odie is a modular always-on voice controlled personal assistant designed for robotics and IoT.',
    long_description=long_description,
    url='https://github.com/drea1989/odie_robo_assistant',
    author='Andrea Balzano',
    author_email='andrea.balzano@live.it',
    license='AGPL-3.0',
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 1 - PoC',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: AGPL-3.0',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Robotics'
        'Topic :: Home Automation',
        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
    ],
    keywords='AI robotics',

    # included packages
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # required libs
    install_requires=[
        'pyyaml>=3.12',
        'six==1.10.0',
        'SpeechRecognition>=3.6.0',
        'markupsafe>=1.0',
        'pyaudio>=0.2.10',
        'pyasn1>=0.2.3',
        'ansible>=2.3',
        py2_prefix + 'pythondialog>=3.4.0',
        'jinja2>=2.8,<=2.9.6',
        'cffi>=1.9.1',
        'ipaddress>=1.0.17',
        'flask>=0.12',
        'Flask-Restful>=0.3.5',
        'flask_cors==3.0.2',
        'requests>=2.13',
        'httpretty>=0.8.14',
        'mock>=2.0.0',
        'Flask-Testing>=0.6.2',
        'apscheduler>=3.3.1',
        'GitPython>=2.1.3',
        'packaging>=16.8',
        'transitions>=0.4.3',
        'sounddevice>=0.3.7',
        'SoundFile>=0.9.0',
        'pyalsaaudio>=0.8.4',
        'RPi.GPIO>=0.6.3',
        'psycopg2>=2.7.1',
        'sqlalchemy>=1.2',
        'pandas>=0.20',
        'sox>=1.3.0'
    ],


    # additional files
    package_data={
        'odie': [
            'brain.yml',
            'settings.yml',
            'wakeon/snowboy/armv7l/python35/_snowboydetect.so',
            'wakeon/snowboy/x86_64/python35/_snowboydetect.so',
            'wakeon/snowboy/resources/*',
            'sounds/*'
         ],
    },

    # entry point script
    entry_points={
        'console_scripts': [
            'odie=odie:main',
        ],
    },
)
