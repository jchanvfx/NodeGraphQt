#!/usr/bin/python
from six import with_metaclass

from ..widgets.node import NodeItem


class NodeMeta(type):
    """
    base meta class type for a NodePlugin
    """

    def __init__(cls, name, bases, attrs):
        """
        Called when a Plugin derived class is imported
        """
        module = str(cls.__module__) + '.' + str(cls.__name__)
        cls.NODE_TYPE = module
        if cls.NODE_NAME is None:
            cls.NODE_NAME = str(cls.__name__)


class NodePlugin(with_metaclass(NodeMeta, object)):
    """
    Base class of a Node.
    """
    NODE_NAME = None
    NODE_TYPE = None

    def __init__(self, node=None):
        self._node_item = node
        if not node:
            self._node_item = NodeItem()
            self._node_item.type = self.type()
            self._node_item.name = self.NODE_NAME
            self.NODE_NAME = self._node_item.name

    def __repr__(self):
        module = str(self.__class__.__module__)
        return '{}.{}(\'{}\')'.format(module, self.NODE_TYPE, self.NODE_NAME)

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
        return self.NODE_TYPE
