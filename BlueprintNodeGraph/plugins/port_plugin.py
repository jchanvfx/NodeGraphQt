#!/usr/bin/python
from BlueprintNodeGraph.widgets.port import PortItem


class PortPlugin(object):

    NODE = None

    def __init__(self, node=None, port=PortItem()):
        if node:
            self.NODE = node
        self._port_item = port

    def __repr__(self):
        module = str(self.__class__.__module__)
        name = str(self.__class__.__name__)
        return module + '.' + name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.node().id() == other.node().id()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.type(), self.node().id()))

    @property
    def item(self):
        """
        returns the PortItem() used in the scene.

        Returns:
            PortItem: port item.
        """
        return self._port_item

    def name(self):
        """
        name of the port.

        Returns:
            str: port name.
        """
        return self.item.name

    def node(self):
        """
        Return the parent node of the port.

        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        return self.NODE

    def type(self):
        """
        Returns the port type.

        Returns:
            str: 'in' for input port or 'out' for output port.
        """
        return self.item.port_type


class PipePlugin(object):

    def __init__(self, pipe=None):
        self. _pipe_item = pipe

    def __repr__(self):
        module = str(self.__class__.__module__)
        name = str(self.__class__.__name__)
        return module + '.' + name

    @property
    def item(self):
        """
        returns the PipeItem() used in the scene.

        Returns:
            PortItem: pipe item.
        """
        return self._pipe_item
