#!/usr/bin/python
from PySide import QtGui

from .node import Node
from .src import node_types
from .src.scene import NodeScene
from .src.viewer import NodeViewer


class NodeGraph(QtGui.QWidget):

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setWindowTitle('Node Graph')
        self._scene = NodeScene()
        self._viewer = NodeViewer(self, self._scene)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._viewer)

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
            nodes (list[BlueprintNodeGraph.Node]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def write(self, path):
        """
        Serialize the current node graph layout.

        Args:
            path (str): file path to be saved.
        """
        self._viewer.write(path)

    def load(self, path):
        """
        Load serialized node graph layout file.

        Args:
            path (str): session file path.
        """
        self._viewer.load(path)

    def create_node(self, class_type, name):
        """
        Create node object.

        Args:
            class_type (str): node class type.
            name (str): name of the node.

        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        node = node_types.get_registered_nodes(class_type)()
        node.set_name(name)
        self.clear_selection()
        node.set_selected(True)
        self.add_node(node)
        return node

    def add_node(self, node):
        """
        Add a node into the node graph.

        Args:
            node (BlueprintNodeGraph.Node): node object.
        """
        assert isinstance(node, Node), 'node must be a Node() object'
        self._viewer.add_node(node.item)

    def delete_node(self, node):
        """
        Removes the node from the node graph.

        Args:
            node (BlueprintNodeGraph.Node): node object.
        """
        assert isinstance(node, Node), 'node must be a Node() object'
        node.delete()

    def all_nodes(self):
        """
        Return all nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        return [Node(node=n) for n in self._viewer.all_nodes()]

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        return [Node(node=n) for n in self._viewer.selected_nodes()]

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
            BlueprintNodeGraph.Node: node object.
        """
        for node_item in self._viewer.all_nodes():
            if node_item.name == name:
                return Node(node=node_item)

    def duplicate_nodes(self, nodes):
        """
        Create duplicates nodes.

        Args:
            nodes (list[BlueprintNodeGraph.Node]): list of node objects.
        """
        self._viewer.duplicate_nodes(nodes)

    def connect_node_to_node(self, from_node, from_port, to_node, to_port):
        """
        Connects a node with a matching node name and port name to another
        node with matching node name and port name.

        Args:
            from_node (str): name of the node.
            from_port (str): name of the node port.
            to_node (str): name of the node.
            to_port (str): name of the node port.
        """
        connection = {}
        for node_item in self._viewer.all_nodes():
            if node_item.name == from_node:
                connection[from_node] = Node(node_item)
            elif node_item.name == to_port:
                connection[to_node] = Node(node_item)
            if connection.get(from_node) and connection.get(to_node):
                break
        if not connection.get(from_node):
            raise Exception('no node named {}'.format(from_node))
        if not connection.get(to_node):
            raise Exception('no node named {}'.format(to_node))
        ports = connection[from_node].inputs() + connection[from_node].outputs()
        for port in ports:
            if port.name() == from_port:
                connection[from_port] = port
                break
        ports = connection[to_node].inputs() + connection[to_node].outputs()
        for port in ports:
            if port.name() == to_port:
                connection[to_port] = port
                break
        if not connection.get(from_port):
            raise Exception('no port {}'.format(from_port))
        if not connection.get(to_port):
            raise Exception('no port {}'.format(to_node))
        connection[from_port].connect_to(connection[to_port])
