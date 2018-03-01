#!/usr/bin/python
from ..interfaces.node import Node
from node_plugin import NodePlugin


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
        node_type (str): NodeGraphQt.nodes.my_nodes.FooNode

    Returns:
        NodePlugin: node class to be instantiated
    """
    return NodePlugin.registered_nodes.get(node_type)
