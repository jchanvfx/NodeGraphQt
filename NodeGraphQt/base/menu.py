#!/usr/bin/python
from distutils.version import LooseVersion

from NodeGraphQt import QtGui, QtCore
from NodeGraphQt.errors import NodeMenuError
from NodeGraphQt.widgets.actions import BaseMenu, GraphAction, NodeAction


class NodeGraphMenu(object):
    """
    The ``NodeGraphMenu`` is the context menu triggered from the node graph.

    example for accessing the node graph context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph

        node_graph = NodeGraph()

        # get the context menu for the node graph.
        context_menu = node_graph.get_context_menu('graph')

        print(context_menu)
        # >> <NodeGraphMenu("NodeGraph") object at 0x10910fdd8>
    """

    def __init__(self, graph, qmenu):
        self._graph = graph
        self._qmenu = qmenu

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.name(), hex(id(self)))

    @property
    def qmenu(self):
        """
        The underlying qmenu.

        Returns:
            BaseMenu: qmenu object.
        """
        return self._qmenu

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
            NodeGraphQt.NodeGraphMenu: menu item.
        """
        menu = self.qmenu.get_menu(name)
        if menu:
            return NodeGraphMenu(self._graph, menu)

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
                return NodeGraphCommand(self._graph, action)

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
        return [NodeGraphCommand(self._graph, a) for a in child_actions]

    def add_menu(self, name):
        """
        Adds a child menu to the current menu.

        Args:
            name (str): menu name.

        Returns:
            NodeGraphQt.NodeGraphMenu: the appended menu item.
        """
        menu = BaseMenu(name, self.qmenu)
        self.qmenu.addMenu(menu)
        return NodeGraphMenu(self._graph, menu)

    def add_command(self, name, func=None, shortcut=None):
        """
        Adds a command to the menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``)".
            shortcut (str): shotcut key.

        Returns:
            NodeGraphQt.MenuCommand: the appended command.
        """
        action = GraphAction(name, self._graph.viewer())
        action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)
        if shortcut:
            action.setShortcut(shortcut)
        if func:
            action.executed.connect(func)
        qaction = self.qmenu.addAction(action)
        return NodeGraphCommand(self._graph, qaction)

    def add_separator(self):
        """
        Adds a separator to the menu.
        """
        self.qmenu.addSeparator()


class NodesMenu(NodeGraphMenu):
    """
    The ``NodesMenu`` is the context menu triggered from the nodes.

    **Inherited from:** :class:`NodeGraphQt.NodeGraphMenu`

    example for adding a command to the nodes context menu.

    .. code-block:: python
        :linenos:

        from NodeGraphQt import BaseNode, NodeGraph

        # example node.
        class MyNode(BaseNode):

            __identifier__ = 'com.chantasticvfx'
            NODE_NAME = 'my node'

            def __init__(self):
                super(MyNode, self).__init__()
                self.add_input('in')
                self.add_output('out')

        # create node graph.
        node_graph = NodeGraph()

        # register example node.
        node_graph.register_node(MyNode)

        # get the context menu for the nodes.
        nodes_menu = node_graph.get_context_menu('nodes')

        # create a command
        def test_func(graph, node):
            print('Clicked on node: {}'.format(node.name()))

        nodes_menu.add_command('test',
                               func=test_func,
                               node_type='com.chantasticvfx.MyNode')

    """

    def add_command(self, name, func=None, node_type=None):
        """
        Re-implemented to add a command to the specified node type menu.

        Args:
            name (str): command name.
            func (function): command function eg. "func(``graph``, ``node``)".
            node_type (str): specified node type for the command.

        Returns:
            NodeGraphQt.MenuCommand: the appended command.
        """
        if not node_type:
            raise NodeMenuError('Node type not specified!')

        node_menu = self.qmenu.get_menu(node_type)
        if not node_menu:
            node_menu = BaseMenu(node_type, self.qmenu)
            self.qmenu.addMenu(node_menu)

        if not self.qmenu.isEnabled():
            self.qmenu.setDisabled(False)

        action = NodeAction(name, self._graph.viewer())
        action.graph = self._graph
        if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
            action.setShortcutVisibleInContextMenu(True)
        if func:
            action.executed.connect(func)
        qaction = node_menu.addAction(action)
        return NodeGraphCommand(self._graph, qaction)


class NodeGraphCommand(object):
    """
    Node graph menu command.
    """

    def __init__(self, graph, qaction):
        self._graph = graph
        self._qaction = qaction

    def __repr__(self):
        return '<{}("{}") object at {}>'.format(
            self.__class__.__name__, self.name(), hex(id(self)))

    @property
    def qaction(self):
        """
        The underlying qaction.

        Returns:
            BaseAction: qaction object.
        """
        return self._qaction

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
