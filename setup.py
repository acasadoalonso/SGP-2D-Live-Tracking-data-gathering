#!/usr/bin/env python3

from os import path
from setuptools import setup, find_packages

#from ogn.client.settings import PACKAGE_VERSION


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aprslog',
    version='2.0',
    description='A python module for the Open Glider Network',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/acasadoalonso/SGP-2D-Live-Tracking-data-gathering', 
    author='Angel Casado', 
    author_email='acasado@acm.org',
    license='AGPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: GIS',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='gliding ogn',
    packages=['ogn.{}'.format(package) for package in find_packages(where='ogn')],
    python_requires='>=3',
    install_requires=[],
    extras_require={
        'dev': [
            'nose==1.3.7',
            'coveralls==2.1.2',
            'flake8==3.8.3'
        ]
    },
    zip_safe=False
)
