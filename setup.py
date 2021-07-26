#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools
from NodeGraphQt import pkg_info

setuptools.setup(
    name=pkg_info.__module_name__,
    version=pkg_info.__version__,
    author=pkg_info.__author__,
    url=pkg_info.__url__,
)


# python3 setup.py sdist
# python3 setup.py install --prefix ~/.local/
