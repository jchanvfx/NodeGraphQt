#!/usr/bin/python
from distutils.version import LooseVersion

from PySide2 import QtGui, QtCore, QtWidgets

from NodeGraphQt.widgets.stylesheet import STYLE_QMENU


class ContextMenu(object):
    """
    base class for a context menu item.
    """

    def __init__(self, viewer, qmenu):
        self.__viewer = viewer
        self.__qmenu = qmenu

    def __repr__(self):
        cls_name = self.__class__.__name__
        return 'NodeGraphQt.{}(\'{}\')'.format(cls_name, self.name())

    @property
    def qmenu(self):
        return self.__qmenu

    def name(self):
        """
        Returns the label for the menu.

        Returns:
            str: label name.
        """
        return self.qmenu.title()

    def get_menu(self, name):
        """
        Returns the child context menu item by name.

        Args:
            name (str): name of the menu.

        Returns:
            NodeGraphQt.base.menu.ContextMenu: menu item.
        """
        for action in self.qmenu.actions():
            if action.menu() and action.menu().title() == name:
                return ContextMenu(self.__viewer, action.menu())

    def get_command(self, name):
        """
        Returns the child menu command item by name.

        Args:
            name (str): name of the command.

        Returns:
            NodeGraphQt.ContextMenuCommand: context menu command.
        """
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return ContextMenuCommand(self.__viewer, action)

    def all_commands(self):
        """
        Returns all child and sub child commands from the current context menu.

        Returns:
            list[NodeGraphQt.ContextMenuCommand]: list of commands.
        """
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
        """
        Adds a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.ContextMenu: the appended menu.
        """
        menu = QtWidgets.QMenu(None, title=name)
        menu.setStyleSheet(STYLE_QMENU)
        self.qmenu.addMenu(menu)
        return ContextMenu(self.__viewer, menu)

    def add_command(self, name, func=None, shortcut=None):
        """
        Adds a command to the menu.

        Args:
            name (str): command name.
            func (): command function.
            shortcut (str): shotcut key.

        Returns:
            NodeGraphQt.ContextMenuCommand: the appended command.
        """
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
        """
        Adds a separator to the menu.
        """
        self.qmenu.addSeparator()


class ContextMenuCommand(object):
    """
    base class for a context menu command.
    """

    def __init__(self, viewer, qaction):
        self.__viewer = viewer
        self.__qaction = qaction

    def __repr__(self):
        cls_name = self.__class__.__name__
        return 'NodeGraphQt.{}(\'{}\')'.format(cls_name, self.name())

    @property
    def qaction(self):
        return self.__qaction

    def name(self):
        """
        Returns the label for the menu command.

        Returns:
            str: label name.
        """
        return self.qaction.text()

    def set_shortcut(self, shortcut=None):
        """
        Sets the shortcut key combination for the menu command.

        Args:
            shortcut (str): shortcut key.
        """
        shortcut = shortcut or QtGui.QKeySequence()
        self.qaction.setShortcut(shortcut)

    def run_command(self):
        """
        execute the menu command.
        """
        self.qaction.trigger()
