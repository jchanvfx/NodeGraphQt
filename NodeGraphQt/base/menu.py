#!/usr/bin/python
from distutils.version import LooseVersion

from NodeGraphQt import QtGui, QtCore, QtWidgets
from NodeGraphQt.errors import NodeMenuError
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

    def set_name(self, name):
        """
        Set the name for the menu.

        Args:
            name (str): label name.
        """
        self.qmenu.setTitle(name)

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

    def get_action(self, name):
        """
        Returns the child menu command by name.

        Args:
            name (str): name of the command.

        Returns:
            NodeGraphQt.MenuCommand: context menu command.
        """
        for action in self.qmenu.actions():
            if not action.menu() and action.text() == name:
                return MenuAction(self.__viewer, action)

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

    def create_menu(self, name):
        """
        Create a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.Menu: the appended menu item.
        """
        menu = QtWidgets.QMenu(name, self.__viewer)
        self.qmenu.addMenu(menu)
        return Menu(self.__viewer, menu)

    def create_action(self, name):
        """
        Create a command to the menu.

        Args:
            name (NodeGraphQt.MenuCommand): menu command.


        """
        action = QtWidgets.QAction(name, self.__viewer)
        qaction = self.qmenu.addAction(action)
        return MenuAction(self.__viewer, qaction)

    def create_separator(self):
        """
        Create a separator to the menu.
        """
        self.qmenu.addSeparator()


class MenuAction(QtWidgets.QAction):
    """
    base class for a menu command.
    """

    #: signal emits when the action has triggered in the node graph.
    executed = QtCore.QSignal(object)

    def __init__(self, parent=None, viewer=None, name=''):
        super(MenuAction, self).__init__(parent)
        self.__viewer = viewer
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            self.setShortcutVisibleInContextMenu(True)
        self.setText(name)
        self.triggered.connect(self._on_triggered)

    def __repr__(self):
        cls_name = self.__class__.__name__
        return 'NodeGraphQt.{}(\'{}\')'.format(cls_name, self.name())

    def _on_triggered(self):
        menu = self.menu()
        pos = self.mapToScene(menu.pos())

        items = self.__viewer._items_near(pos)
        

        self.triggered.emit()

    def name(self):
        """
        Returns the name for the menu command.

        Returns:
            str: label name.
        """
        return self.text()

    def set_name(self, name):
        """
        Set the name for the menu command.

        Args:
            name (str): label name.
        """
        self.setText(name)

    def set_shortcut(self, shortcut=None):
        """
        Sets the shortcut key combination for the menu command.

        Args:
            shortcut (str): shortcut key.
        """
        shortcut = shortcut or QtGui.QKeySequence()
        self.qaction.setShortcut(shortcut)
