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


class NodeStateUndoCommand(QtGui.QUndoCommand):

    def __init__(self, node):
        super(NodeStateUndoCommand, self).__init__(self)
        self.setText('modified properties')
        self.node = node


class NodePosUndoCommand(QtGui.QUndoCommand):

    def __init__(self, node):
        super(NodePosUndoCommand, self).__init__(self)
        self.setText('update node position')
        self.node = node
        self.pos = (node.pos().x(), node.pos().y())

    def undo(self):
        x, y = self.pos
        self.node.setPos(x, y)

    def redo(self):
        x, y = self.pos
        self.node.setPos(x, y)
