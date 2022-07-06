#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools

from NodeGraphQt import pkg_info

if __name__ == '__main__':
    setuptools.setup(
        name=pkg_info.__module_name__,
        version=pkg_info.__version__,
        author=pkg_info.__author__,
    )
