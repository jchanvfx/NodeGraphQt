#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

import setuptools

sys.path.append(os.path.join(os.path.dirname(__file__), "NodeGraphQt"))

import pkg_info

with open('README.md', 'r') as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

description = (
    'Node graph framework that can be re-implemented into applications that '
    'supports PySide & PySide2'
)
classifiers = [
    'Operating System :: OS Independent',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    'Documentation :: https://jchanvfx.github.io/NodeGraphQt/api/html/index.html',
    'Source :: https://github.com/jchanvfx/NodeGraphQt/',
]

setuptools.setup(
    name=pkg_info.__module_name__,
    version=pkg_info.__version__,
    author=pkg_info.__author__,
    author_email='',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=pkg_info.__url__,
    packages=setuptools.find_packages(exclude=['example_nodes']),
    classifiers=classifiers,
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.6',
    extras_require={
        'PySide2': ['PySide2>=5.12']
    }
)


"""
python setup.py sdist
sudo python setup.py install
"""
