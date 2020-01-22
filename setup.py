#!/usr/bin/python
# -*- coding: utf-8 -*-
import setuptools

import NodeGraphQt.pkg_info as pkg_info

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
    'Programming Language :: Python :: 3.7',
    'Documentation :: https://jchanvfx.github.io/NodeGraphQt/api/html/index.html',
    'Source :: https://github.com/jchanvfx/NodeGraphQt/',
]

setuptools.setup(
    name=pkg_info.__module_name__,
    version=pkg_info.__version__,
    author=pkg_info.__author__,
    author_email=pkg_info.__email__,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=pkg_info.__url__,
    packages=setuptools.find_packages(exclude=['example_nodes']),
    classifiers=classifiers,
    install_requires=requirements,
    include_package_data=True,
    python_requires='>=3.7'
)


"""
python setup.py sdist
sudo python setup.py install
"""
