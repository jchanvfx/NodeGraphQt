#!/usr/bin/python

from BlueprintNodeGraph.port import PortItem


class Port(object):
    def __init__(self, port=PortItem()):
        self._port_item = port

    def __str__(self):
        name = self.__class__.__name__
        return '{}(name={}, node={})'.format(name, self.name(), self.node())

    def name(self):
        """
        name of the port.

        Returns:
            str: port name.
        """
        return self._port_item.name

    def node(self):
        """
        Return the parent node of the port.

        Returns:
            BlueprintNodeGraph.Node: node object.
        """
        return Node(self._port_item.node)

    def type(self):
        """
        Returns the port type.

        Returns:
            str: 'in' for input port or 'out' for output port.
        """
        return self._port_item.port_type

    def color(self):
        """
        Returns the default port color.

        Returns:
            tuple: (r, g, b, a) from 0-255 range.
        """
        return self._port_item.color

    def set_color(self, color):
        """
        Sets the default port color in (red, green, blur, alpha) value.

        Args:
            color (tuple): (r, g, b, a) from 0-255 range.
        """
        self._port_item.color = color

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[BlueprintNodeGraph.Port]: list pf connected ports.
        """
        ports = []
        for port in self._port_item.connected_ports:
            port.append(Port(port))
        return ports

    def connect_to(self, port=None):
        """
        Creates a pipe and connects it to the port with a connection.

        Args:
            port (BlueprintNodeGraph.Port): port object.
        """
        port_item = port._port_item
        if not isinstance(port_item, PortItem):
            return
        viewer = self._port_item.scene().viewer()
        viewer.connect_ports(self._port_item, port_item)

        # def disconnect_from(self, port=None):
        #     port_item = port._port_item
        #     if not isinstance(port_item, PortItem):
        #         return
