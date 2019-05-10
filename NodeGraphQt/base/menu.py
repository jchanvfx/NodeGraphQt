#!/usr/bin/python
from distutils.version import LooseVersion

from NodeGraphQt import QtGui, QtCore, QtWidgets
from NodeGraphQt.widgets.stylesheet import STYLE_QMENU


class Menu(object):
    """
    base class for a menu item.
    """

    def __init__(self, viewer, qmenu):
        self.__viewer = viewer
        self.__qmenu = qmenu

    def __repr__(self):
        cls_name = self.__class__.__name__
        return '<{}("{}") object at {}>'.format(cls_name, self.name(), hex(id(self)))

    @property
    def qmenu(self):
        return self.__qmenu

    def name(self):
        """
        Returns the name for the menu.

        Returns:
            str: label name.
        """
        return self.qmenu.title()

    def get_menu(self, name):
        """
        Returns the child menu by name.

        Args:
            name (str): name of the menu.

        Returns:
            NodeGraphQt.Menu: menu item.
        """
        for action in self.qmenu.actions():
            if action.menu() and action.menu().title() == name:
                return Menu(self.__viewer, action.menu())

    def get_command(self, name):
        """
        Returns the child menu command by name.

        Args:
            name (str): name of the command.

        Returns:
            NodeGraphQt.MenuCommand: context menu command.
        """
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return MenuCommand(self.__viewer, action)

    def all_commands(self):
        """
        Returns all child and sub child commands from the current context menu.

        Returns:
            list[NodeGraphQt.MenuCommand]: list of commands.
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
        return [MenuCommand(self.__viewer, a) for a in child_actions]

    def add_menu(self, name):
        """
        Adds a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.Menu: the appended menu item.
        """
        menu = QtWidgets.QMenu(name, self.qmenu)
        menu.setStyleSheet(STYLE_QMENU)
        self.qmenu.addMenu(menu)
        return Menu(self.__viewer, menu)

    def add_command(self, name, func=None, shortcut=None):
        """
        Adds a command to the menu.

        Args:
            name (str): command name.
            func (function): command function.
            shortcut (str): function shotcut key.

        Returns:
            NodeGraphQt.MenuCommand: the appended command.
        """
        action = QtWidgets.QAction(name, self.__viewer)
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)
        if shortcut:
            action.setShortcut(shortcut)
        if func:
            action.triggered.connect(func)
        qaction = self.qmenu.addAction(action)
        return MenuCommand(self.__viewer, qaction)

    def add_separator(self):
        """
        Adds a separator to the menu.
        """
        self.qmenu.addSeparator()


class MenuCommand(object):
    """
    base class for a menu command.
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
        Returns the name for the menu command.

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
