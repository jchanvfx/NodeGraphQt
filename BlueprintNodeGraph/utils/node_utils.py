#!/usr/bin/python
import os
from BlueprintNodeGraph.plugins.node_plugin import NodePlugin
from BlueprintNodeGraph.interfaces.node import Node

os.environ['BP_NODE_PLUGINS'] = []


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


# TODO implement plugin path system.
def add_plugin_path(plugin_path):
    plugin_paths = os.getenv('BP_NODE_PLUGINS')
    if os.path.isdir(plugin_path) and plugin_path not in plugin_paths:
        plugin_paths.append(plugin_path)
        os.environ['BP_NODE_PLUGINS'] = plugin_paths


def load_plugins():
    if os.getenv('BP_NODE_PLUGINS'):
        for plugin in os.getenv('BP_NODE_PLUGINS'):
            print plugin
