#!/usr/bin/python
import os
import sys
import ast


VALID_NODE_TYPE = ['BaseNode', 'AutoNode']


def detectNodesFromText(filepath):
    """returns Node names from a python script"""
    froms = []

    with open(filepath, "r") as source:
        tree = ast.parse(source.read())
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if base.id in VALID_NODE_TYPE:
                    for indef in node.body:
                        if isinstance(indef, ast.Assign):
                            for target in indef.targets:
                                if target.id == '__identifier__':
                                    froms.append(node.name)
    return froms


def getNodesRecursively(path=__file__):
    """ Returns imported nodes. """
    Nodes = []
    basedir, filename = os.path.split(path)
    rootModule = os.path.basename(basedir)

    for root, dirs, files in os.walk(basedir, topdown=False):
        if root not in sys.path:
            sys.path.append(root)

        for name in files:
            if name.endswith('.py') and not name.startswith('_'):
                module_name = root.split(rootModule)[1].replace('\\', '.') + name[:-3]
                modulePath = os.path.join(root, name)
                froms = detectNodesFromText(modulePath)
                if not froms:
                    continue

                try:
                    mod = __import__(module_name, globals(), locals(), froms, 0)
                    for node in froms:
                        Nodes.append(getattr(mod, node))

                except ImportError as e:
                    print ('Error in importing class: %s' % (e))
                    continue

    return Nodes


Nodes = getNodesRecursively()
