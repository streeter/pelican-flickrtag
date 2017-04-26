#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import pelican_flickrtag


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_wheel upload')
    sys.exit()


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

packages = [
    'pelican_flickrtag',
]

requires = [
    'jinja2',
    'pelican',
]

setup(
    name='pelican-flickrtag',
    version=pelican_flickrtag.__version__,
    description='Display Flickr images easily in your Pelican articles.',
    long_description=readme,
    author='Chris Streeter',
    author_email='chris@chrisstreeter.com',
    url='https://github.com/streeter/pelican-flickrtag',
    packages=packages,
    package_data={'': ['LICENSE', ]},
    package_dir={'pelican_flickrtag': 'pelican_flickrtag'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
    ],
)
