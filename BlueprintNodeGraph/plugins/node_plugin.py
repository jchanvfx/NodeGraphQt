#!/usr/bin/python
from BlueprintNodeGraph.widgets.node import NodeItem


class NodeMeta(type):
    """
    base meta class type for a NodePlugin
    """

    def __init__(cls, name, bases, attrs):
        """
        Called when a Plugin derived class is imported
        """
        if not hasattr(cls, 'registered_nodes'):
            # Called when the metaclass is first instantiated
            cls.registered_nodes = {}
        else:
            # Called when a plugin class is imported
            cls.register_node(cls)

    def register_node(cls, plugin):
        """
        Store node plugin module import to a module reference.

        Args:
            plugin (NodeMeta): node plugin meta.
        """
        module = str(plugin.__module__) + '.' + str(plugin.NODE_TYPE)
        cls.registered_nodes[module] = plugin


class NodePlugin(object):
    """
    Base class of a Node.
    """
    __metaclass__ = NodeMeta
    NODE_NAME = 'node'
    NODE_TYPE = 'Node'

    def __init__(self, node=None):
        self._node_item = node
        if not node:
            self._node_item = NodeItem()

    def __repr__(self):
        module = str(self.__class__.__module__)
        return '{}.{}(\'{}\')'.format(module, self.NODE_TYPE)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id() == other.id()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type(), self.id()))

    @property
    def item(self):
        """
        returns the NodeItem() used in the scene.

        Returns:
            NodeItem: node item.
        """
        return self._node_item

    def id(self):
        """
        The node unique id.

        Returns:
            str: UUID of the node.
        """
        return self.item.id

    def type(self):
        """
        returns the node type.

        Returns:
            str: node type.
        """
        module = str(self.__class__.__module__)
        return module + '.' + self.NODE_TYPE
