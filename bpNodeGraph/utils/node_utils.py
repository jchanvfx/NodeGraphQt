#!/usr/bin/python
from PySide import QtGui
from ..interfaces.node import Node
from ..plugins.node_plugin import NodePlugin


def get_registered_nodes():
    """
    returns all registered node plugins.

    Returns:
        dict: {node_type: node_class}
    """
    nodes = sorted(NodePlugin.registered_nodes.keys())
    exclude = str(Node.__module__) + '.' + str(Node.NODE_TYPE)
    if exclude in nodes:
        nodes.remove(exclude)
    return nodes


def get_node(node_type):
    """
    return a node object from the node type.

    Args:
        node_type (str): BlueprintNodeGraph.nodes.my_nodes.FooNode

    Returns:
        NodePlugin: node class to be instantiated
    """
    return NodePlugin.registered_nodes.get(node_type)


class NodeUndoPosition(QtGui.QUndoCommand):

    def __init__(self, nodes, from_pos, to_pos):
        super(NodeUndoPosition, self).__init__(self)
        self.setText('move node')
        self.nodes = nodes
        self.from_pos = from_pos
        self.to_pos = to_pos

    def undo(self):
        for idx, node in enumerate(self.nodes):
            x, y = self.from_pos[idx]
            node.setPos(x, y)

    def redo(self):
        for idx, node in enumerate(self.nodes):
            x, y = self.to_pos[idx]
            node.setPos(x, y)
