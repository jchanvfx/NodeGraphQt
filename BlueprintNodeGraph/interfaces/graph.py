#!/usr/bin/python
from PySide import QtGui

from BlueprintNodeGraph.scene import NodeScene
from BlueprintNodeGraph.viewer import NodeViewer
from .node import Node


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

    def center_on(self, nodes=None):
        """
        Center the node graph on the given nodes or all nodes by default.

        Args:
            nodes (list[BlueprintNodeGraph.Node]): a list of nodes.
        """
        self._viewer.center_selection(nodes)

    def save(self, path):
        """
        Save out the current node graph session with a ".ngraph" file extension.

        Args:
            path (str): file path to be saved.
        """
        self._viewer.save_session(path, False)

    def load(self, path):
        """
        Open node graph session file.

        Args:
            path (str): session file path.
        """
        self._viewer.load_session(path, False)

    def add_node(self, node):
        """
        Add a node into the node graph.

        Args:
            node (BlueprintNodeGraph.Node): node object.
        """
        assert isinstance(node, Node), 'node must be a Node() object'
        self._viewer.add_node(node._node_item)

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
        nodes = []
        for node in self._viewer.all_nodes():
            nodes.append(Node(node=node._node_item))
        return nodes

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        nodes = []
        for node in self._viewer.selected_nodes():
            nodes.append(Node(node=node._node_item))
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
            BlueprintNodeGraph.Node: node object.
        """
        for node_item in self._viewer.all_nodes():
            if node_item.name == name:
                return Node(node=node_item)

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
