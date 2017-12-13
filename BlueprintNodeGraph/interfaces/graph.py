#!/usr/bin/python
from PySide import QtGui

from BlueprintNodeGraph.plugins.node_plugin import NodePlugin
from BlueprintNodeGraph.utils.node_utils import get_node
from BlueprintNodeGraph.widgets.scene import NodeScene
from BlueprintNodeGraph.widgets.viewer import NodeViewer


_NODES_LOADED = False


class NodeGraph(QtGui.QWidget):

    def __init__(self, parent=None):
        super(NodeGraph, self).__init__(parent)
        self.setWindowTitle('Node Graph')
        self._scene = NodeScene()
        self._viewer = NodeViewer(self, self._scene)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._viewer)

        # TODO: find a better way of loading nodes.
        global _NODES_LOADED
        if not _NODES_LOADED:
            _NODES_LOADED = True
            import BlueprintNodeGraph.nodes

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

    def create_node(self, node_type, name):
        """
        Create node object.

        Args:
            node_type (str): node class type.
            name (str): name of the node.

        Returns:
            BlueprintNodeGraph.Node: node instance.
        """
        NodeInstance = get_node(node_type)
        if NodeInstance:
            node = NodeInstance()
            self.clear_selection()
            self.add_node(node)
            node.set_name(name)
            node.set_selected(True)
            return node
        raise Exception('\n\n>> Cannot find node:\t"{}"\n'.format(node_type))

    def add_node(self, node):
        """
        Add a node into the node graph.

        Args:
            node (BlueprintNodeGraph.interface.Node): node instance.
        """
        assert isinstance(node, NodePlugin), 'node must be a node'
        self._viewer.add_node(node.item)

    def delete_node(self, node):
        """
        Remove the node from the node graph.

        Args:
            node (BlueprintNodeGraph.interface.Node): node object.
        """
        assert isinstance(node, NodePlugin), 'node must be a node'
        node.delete()

    def all_nodes(self):
        """
        Return all nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        nodes = []
        for node_item in self._viewer.all_nodes():
            NodeInstance = get_node(node_item.type)
            nodes.append(NodeInstance(item=node_item))
        return nodes

    def selected_nodes(self):
        """
        Return all selected nodes that are in the node graph.

        Returns:
            list[BlueprintNodeGraph.Node]: list of nodes.
        """
        nodes = []
        for node_item in self._viewer.selected_nodes():
            NodeInstance = get_node(node_item.type)
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
            BlueprintNodeGraph.Node: node object.
        """
        for node_item in self._viewer.all_nodes():
            if node_item.name == name:
                NodeInstance = get_node(node_item.type)
                return NodeInstance(item=node_item)

    def duplicate_nodes(self, nodes):
        """
        Create duplicates nodes.

        Args:
            nodes (list[BlueprintNodeGraph.Node]): list of node objects.
        """
        self._viewer.duplicate_nodes(nodes)
