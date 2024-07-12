#!/usr/bin/python
import re
from distutils.version import LooseVersion

from Qt import QtGui, QtCore

from NodeGraphQt.errors import NodeMenuError
from NodeGraphQt.widgets.actions import BaseMenu, GraphAction, NodeAction


class NodeGraphMenu(object):
    """
    The ``NodeGraphMenu`` is the main context menu triggered from the node graph.

    .. inheritance-diagram:: NodeGraphQt.NodeGraphMenu
        :parts: 1

    example for accessing the node graph context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph

        node_graph = NodeGraph()

        # get the context menu for the node graph.
        context_menu = node_graph.get_context_menu('graph')

    """

    def __init__(self, graph, qmenu):
        self._graph = graph
        self._qmenu = qmenu
        self._name = qmenu.title()
        self._menus = {}
        self._commands = {}
        self._items = []

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.name(), hex(id(self)))

    @property
    def qmenu(self):
        """
        The underlying QMenu.

        Returns:
            BaseMenu: menu object.
        """
        return self._qmenu

    def name(self):
        """
        Returns the name for the menu.

        Returns:
            str: label name.
        """
        return self._name

    def get_items(self):
        """
        Return the menu items in the order they were added.

        Returns:
            list: current menu items.
        """
        return self._items

    def get_menu(self, name):
        """
        Returns the child menu by name.

        Args:
            name (str): name of the menu.

        Returns:
            NodeGraphQt.NodeGraphMenu: menu item.
        """
        self._menus.get(name)

    def get_command(self, name):
        """
        Returns the child menu command by name.

        Args:
            name (str): name of the command.

        Returns:
            NodeGraphQt.NodeGraphCommand: context menu command.
        """
        return self._commands.get(name)

    def add_menu(self, name):
        """
        Adds a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu: the appended menu item.
        """
        if name in self._menus:
            raise NodeMenuError('menu object "{}" already exists!'.format(name))
        base_menu = BaseMenu(name, self.qmenu)
        self.qmenu.addMenu(base_menu)
        menu = NodeGraphMenu(self._graph, base_menu)
        self._menus[name] = menu
        self._items.append(menu)
        return menu

    @staticmethod
    def _set_shortcut(action, shortcut):
        if isinstance(shortcut, str):
            search = re.search(r'(?:\.|)QKeySequence\.(\w+)', shortcut)
            if search:
                shortcut = getattr(QtGui.QKeySequence, search.group(1))
            elif all([i in ['Alt', 'Enter'] for i in shortcut.split('+')]):
                shortcut = QtGui.QKeySequence(
                    QtCore.Qt.ALT | QtCore.Qt.Key_Return
                )
            elif all([i in ['Return', 'Enter'] for i in shortcut.split('+')]):
                shortcut = QtCore.Qt.Key_Return
        if shortcut:
            action.setShortcut(shortcut)

    def add_command(self, name, func=None, shortcut=None):
        """
        Adds a command to the menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``)".
            shortcut (str): shortcut key.

        Returns:
            NodeGraphQt.NodeGraphCommand: the appended command.
        """
        action = GraphAction(name, self._graph.viewer())
        action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)

        if shortcut:
            self._set_shortcut(action, shortcut)
        if func:
            action.executed.connect(func)
        self.qmenu.addAction(action)
        command = NodeGraphCommand(self._graph, action, func)
        self._commands[name] = command
        self._items.append(command)
        return command

    def add_separator(self):
        """
        Adds a separator to the menu.
        """
        self.qmenu.addSeparator()
        self._items.append(None)


class NodesMenu(NodeGraphMenu):
    """
    The ``NodesMenu`` is the context menu triggered from a node.

    .. inheritance-diagram:: NodeGraphQt.NodesMenu
        :parts: 1

    example for accessing the nodes context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph

        node_graph = NodeGraph()

        # get the nodes context menu.
        nodes_menu = node_graph.get_context_menu('nodes')
    """

    def add_command(self, name, func=None, node_type=None, node_class=None,
                    shortcut=None):
        """
        Re-implemented to add a command to the specified node type menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``, ``node``)".
            node_type (str): specified node type for the command.
            node_class (class): specified node class for the command.
            shortcut (str): shortcut key.

        Returns:
            NodeGraphQt.NodeGraphCommand: the appended command.
        """
        if not node_type and not node_class:
            raise NodeMenuError('Node type or Node class not specified!')

        if node_class:
            node_type = node_class.__name__

        node_menu = self.qmenu.get_menu(node_type)
        if not node_menu:
            node_menu = BaseMenu(node_type, self.qmenu)

            if node_class:
                node_menu.node_class = node_class
                node_menu.graph = self._graph

            self.qmenu.addMenu(node_menu)

        if not self.qmenu.isEnabled():
            self.qmenu.setDisabled(False)

        action = NodeAction(name, self._graph.viewer())
        action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)

        if shortcut:
            self._set_shortcut(action, shortcut)
        if func:
            action.executed.connect(func)

        if node_class:
            node_menus = self.qmenu.get_menus(node_class)
            if node_menu in node_menus:
                node_menus.remove(node_menu)
            for menu in node_menus:
                menu.addAction(action)

        node_menu.addAction(action)
        command = NodeGraphCommand(self._graph, action, func)
        self._commands[name] = command
        self._items.append(command)
        return command


class NodeGraphCommand(object):
    """
    Node graph menu command.

    .. inheritance-diagram:: NodeGraphQt.NodeGraphCommand
        :parts: 1

    """

    def __init__(self, graph, qaction, func=None):
        self._graph = graph
        self._qaction = qaction
        self._name = qaction.text()
        self._func = func

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.name(), hex(id(self)))

    @property
    def qaction(self):
        """
        The underlying qaction.

        Returns:
            GraphAction: qaction object.
        """
        return self._qaction

    @property
    def slot_function(self):
        """
        The function executed by this command.

        Returns:
            function: command function.
        """
        return self._func

    def name(self):
        """
        Returns the name for the menu command.

        Returns:
            str: label name.
        """
        return self._name

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

    def set_enabled(self, state):
        """
        Sets the command to either be enabled or disabled.

        Args:
            state (bool): true to enable.
        """
        self.qaction.setEnabled(state)

    def set_hidden(self, hidden):
        """
        Sets then command item visibility in the context menu.

        Args:
            hidden (bool): true to hide the command item.
        """
        self.qaction.setVisible(not hidden)

    def show(self):
        """
        Set the command to be visible in the context menu.
        """
        self.qaction.setVisible(True)

    def hide(self):
        """
        Set the command to be hidden in the context menu.
        """
        self.qaction.setVisible(False)
