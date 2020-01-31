#!/usr/bin/python
import os
import sys
import inspect
import importlib


def getNodesRecursively(path=__file__):
    Nodes = []
    basedir, filename = os.path.split(path)
    for root, dirs, files in os.walk(basedir, topdown=False):
        if root not in sys.path:
            sys.path.append(root)

        for name in files:
            if name.endswith('.py') and not name.startswith('_'):
                module_name = name[:-3]
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and not obj.__name__ == 'BaseNode':
                        for clsObj in inspect.getmro(obj):
                            if clsObj.__name__ == 'BaseNode':
                                Nodes.append(obj)
                                break
    return Nodes


Nodes = getNodesRecursively()
