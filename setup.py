#!/usr/bin/env python

import os
import sys

import flickrtag

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'flickrtag',
]

requires = [
]

setup(
    name='flickrtag',
    version=flickrtag.__version__,
    description='Display Flickr images easily in your Pelican articles.',
    long_description=open('README.md').read(),
    author='Chris Streeter',
    author_email='chris@chrisstreeter.com',
    url='https://github.com/streeter/pelican-flickrtag',
    packages=packages,
    package_data={'': ['LICENSE', ]},
    package_dir={'flickrtag': 'flickrtag'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
