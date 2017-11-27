#!/usr/bin/python

from BlueprintNodeGraph.plugins.node_plugin import NodePlugin


def get_registered_nodes():
    """
    returns all registered node plugins.

    Returns:
        dict: {node_type: node_class}
    """
    return sorted(NodePlugin.registered_nodes.keys())


def get_node(node_type):
    """
    return a node object from the node type.

    Args:
        node_type (str): BlueprintNodeGraph.nodes.my_nodes.FooNode

    Returns:
        NodePlugin: node class to be instantiated
    """
    return NodePlugin.registered_nodes.get(node_type)
