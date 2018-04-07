#!/usr/bin/python
from PySide import QtGui

from ..base.node_vendor import NodeVendor
from ..base.node_plugin import NodePlugin
from ..widgets.scene import NodeScene
from ..widgets.viewer import NodeViewer
from ..interfaces.node import Backdrop


class NodeGraphWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(NodeGraphWidget, self).__init__(parent)
        self.setWindowTitle('Node Graph')
        self._scene = NodeScene()
        self._viewer = NodeViewer(self, self._scene)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._viewer)

        if Backdrop not in NodeVendor.nodes.values():
            NodeVendor.register_node(Backdrop, 'Backdrop')

        self._viewer.search_triggered.connect(self._on_search)

    def _on_search(self, node_type, pos):
        node = self.create_node(node_type)
        node.set_pos(*pos)

    def viewer(self):
        """
        return the viewer object.

        Returns:
            NodeGraphQt.widgets.viewer.NodeViewer: viewer object.
        """
        return self._viewer

    def scene(self):
        """
        return the scene object.

        Returns:
            NodeGraphQt.widgets.scene.NodeScene: scene used for the nodes.
        """
        return self._scene

    def add_menu(self, name, menu):
        """
        Add a menu to the node graph context menu.

        Args:
            name (str): menu name
            menu (QtGui.QMenu): menu object
        """
        if not self._viewer.get_menu(name):
            raise KeyError('name "{}" already exists.'.format(name))
        self._viewer.add_menu(name, menu)

    def get_menu(self, name):
        """
        Returns the node graph menu.

        Returns:
            QtGui.QMenu: menu from the name.
        """
        return self._viewer.get_menu(name)

    def set_acyclic(self, mode=True):
        """
        Set the node graph to be acyclic or not.

        Args:
            mode (bool): false to disable acyclic.
        """
        self._viewer.acyclic = mode

    def set_pipe_layout(self, layout='curved'):
        """
        Set node graph pipes to be drawn straight or curved by default
        all pipes are set curved.

        Args:
            layout (str): 'straight' or 'curved'
        """
        self._viewer.set_pipe_layout(layout)

    def set_zoom(self, zoom=0):
        """
        Set the zoom factor of the Node Graph the default is 0.

        Args:
            zoom (int): zoom factor max zoom out -10 max zoom in 10.
        """
        self._viewer.set_zoom(zoom)

    def get_zoom(self):
        """
        Get the zoom level of the node graph.

        Returns:
            int: the current zoom level.
        """
        return self._viewer.get_zoom()

    def center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[NodeGraphQt.Node]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def center_selection(self):
        """
        Center the node graph on the current selected nodes.
        """
        nodes = self._viewer.selected_nodes()
        self._viewer.center_selection(nodes)

    def save(self, path):
        """
        Saves the current node graph session layout.

        Args:
            path (str): file path to be saved.
        """
        self._viewer.save(path)

    def load(self, path):
        """
        Load node graph session layout file.

        Args:
            path (str): path to the session file.
        """
        self._viewer.load(path)

    def clear(self):
        """
        Clears the node graph.
        """
        self._viewer.clear()

    def registered_nodes(self):
        """
        Return a list of all node types that have been registered.

        Returns:
            list[str]: node types.
        """
        return sorted(NodeVendor.nodes.keys())

    def register_node(self, node, alias=None):
        """
        Register a node.

        Args:
            node (NodeGraphQt.Node): node instance.
            alias (str): custom alias name for the node type.
        """
        NodeVendor.register_node(node, alias)

    def create_node(self, node_type, name=None, selected=True, color=None):
        """
        Create a new node in the node graph.

        Args:
            node_type (str): node class type.
            name (str): set the name for the created node.
            selected (bool): set created node to be selected.
            color (tuple): set the color for the created node (r, g, b).

        Returns:
            NodeGraphQt.Node: node instance.
        """
        NodeInstance = NodeVendor.create_node_instance(node_type)
        if NodeInstance:
            self.clear_selection()
            node = NodeInstance()
            if name:
                node.set_name(name)
            if selected:
                node.set_selected(True)
            if color:
                node.set_color(*color)

            self.add_node(node)
            return node
        raise Exception('\n\n>> Cannot find node:\t"{}"\n'.format(node_type))

    def add_node(self, node):
        """
        Add a node into the node graph.

        Args:
            node (NodeGraphQt.interface.Node): node instance.
        """
        assert isinstance(node, NodePlugin), 'node must be a Node instance.'
        self._viewer.add_node(node.item)

    def delete_node(self, node):
        """
        Remove the node from the node graph.

        Args:
            node (NodeGraphQt.interface.Node): node object.
        """
        assert isinstance(node, NodePlugin), 'node must be a Node instance.'
        node.delete()

    def all_nodes(self):
        """
        Return all nodes that are in the node graph.

        Returns:
            list[NodeGraphQt.Node]: list of nodes.
        """
        nodes = []
        for node_item in self._viewer.all_nodes():
            NodeInstance = NodeVendor.create_node_instance(node_item.type)
            nodes.append(NodeInstance(item=node_item))
        return nodes

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[NodeGraphQt.Node]: list of nodes.
        """
        nodes = []
        for node_item in self._viewer.selected_nodes():
            NodeInstance = NodeVendor.create_node_instance(node_item.type)
            nodes.append(NodeInstance(item=node_item))
        return nodes

    def select_all(self):
        """
        Select all nodes in the current node graph.
        """
        self._viewer.select_all_nodes()

    def clear_selection(self):
        """
        Clears the selection in the node graph.
        """
        self._viewer.clear_selection()

    def get_node(self, name):
        """
        Returns a node object that matches the name.

        Args:
            name (str): name of the node.
        Returns:
            NodeGraphQt.Node: node object.
        """
        for node_item in self._viewer.all_nodes():
            if node_item.name == name:
                node_type = node_item.type
                node_instance = NodeVendor.create_node_instance(node_type)
                return node_instance(item=node_item)

    def duplicate_nodes(self, nodes):
        """
        Create duplicates nodes.

        Args:
            nodes (list[NodeGraphQt.Node]): list of node objects.
        Returns:
            list[NodeGraphQt.Node]: list of duplicated node instances.
        """
        new_nodes = []
        duplicated_nodes = self._viewer.duplicate_nodes(nodes)
        for node in duplicated_nodes:
            node_instance = NodeVendor.create_node_instance(node.type)
            new_nodes.append(node_instance)
        return new_nodes
