#!/usr/bin/python
from distutils.version import LooseVersion

from PySide2 import QtGui, QtCore, QtWidgets

from NodeGraphQt.widgets.stylesheet import STYLE_QMENU


class ContextMenu(object):

    def __init__(self, viewer, qmenu):
        """
        Args:
            viewer (NodeViewer): node viewer.
            qaction (QtWidgets.QMenu): menu object.
        """
        self.__viewer = viewer
        self.__qmenu = qmenu

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '{}.{}(\'{}\')'.format(self.__module__, cls_name, self.name())

    @property
    def qmenu(self):
        return self.__qmenu

    def name(self):
        return self.qmenu.title()

    def get_menu(self, name):
        for action in self.qmenu.actions():
            if action.menu() and action.menu().title() == name:
                return ContextMenu(self.__viewer, action.menu())

    def get_command(self, name):
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return ContextMenuCommand(self.__viewer, action)

    def all_commands(self):
        def get_actions(menu):
            actions = []
            for action in menu.actions():
                if not action.menu():
                    if not action.isSeparator():
                        actions.append(action)
                else:
                    actions += get_actions(action.menu())
            return actions
        child_actions = get_actions(self.qmenu)
        return [ContextMenuCommand(self.__viewer, a) for a in child_actions]

    def add_menu(self, name):
        menu = QtWidgets.QMenu(None, title=name)
        menu.setStyleSheet(STYLE_QMENU)
        self.qmenu.addMenu(menu)
        return ContextMenu(self.__viewer, menu)

    def add_command(self, name, func=None, shortcut=None):
        action = QtWidgets.QAction(name, self.__viewer)
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)
        if shortcut:
            action.setShortcut(shortcut)
        if func:
            action.triggered.connect(func)
        qaction = self.qmenu.addAction(action, shortcut=shortcut)
        return ContextMenuCommand(self.__viewer, qaction)

    def add_separator(self):
        self.qmenu.addSeparator()

    def add_action(self, qaction):
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            qaction.setShortcutVisibleInContextMenu(True)
        self.qmenu.addAction(qaction)


class ContextMenuCommand(object):

    def __init__(self, viewer, qaction):
        """
        Args:
            viewer (NodeViewer): node viewer.
            qaction (QtWidgets.QAction): action object.
        """
        self.__viewer = viewer
        self.__qaction = qaction

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '{}.{}(\'{}\')'.format(self.__module__, cls_name, self.name())

    @property
    def qaction(self):
        return self.__qaction

    def name(self):
        return self.qaction.text()

    def set_shortcut(self, shortcut=None):
        shortcut = shortcut or QtGui.QKeySequence()
        self.qaction.setShortcut(shortcut)
