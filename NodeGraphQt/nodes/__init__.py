#!/usr/bin/python
# import os
# import sys
#
# this_path = os.path.dirname(os.path.abspath(__file__))
# directory = os.listdir(this_path)
# modules = {}
# for pkg_file in directory:
#     pkg, ext = os.path.splitext(pkg_file)
#     if pkg == '__init__':
#         continue
#     if ext in ('.py', '.pyc'):
#         modules[pkg] = ('from . import {}'.format(pkg))
#     elif os.path.isdir(os.path.join(directory, pkg_file)):
#         modules[pkg] = 'from . import {}'.format(pkg)
#
# for pkg, pkg_imp in modules.items():
#     try:
#         exec pkg_imp
#     except Exception as e:
#         import traceback
#         sys.stderr.write('Can\'t import module: {}'.format(pkg))
#         info = sys.exc_info()
#         type = info[0]
#         param = info[1]
#         tb = info[2]
#         traceback.print_exception(type, param, tb, file=sys.stderr)
