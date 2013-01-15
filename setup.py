#!/usr/bin/env python

import os
import sys

import pelican_flickrtag

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

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
    long_description=open('README.rst').read(),
    author='Chris Streeter',
    author_email='chris@chrisstreeter.com',
    url='https://github.com/streeter/pelican-flickrtag',
    packages=packages,
    package_data={'': ['LICENSE', ]},
    package_dir={'pelican_flickrtag': 'pelican_flickrtag'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing',
    ),
)
