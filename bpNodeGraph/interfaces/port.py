#!/usr/bin/python
from ..base.port_plugin import PipePlugin
from ..base.port_plugin import PortPlugin


class Port(PortPlugin):

    def color(self):
        """
        Returns the default port color (red, green, blue).

        Returns:
            tuple: (r, g, b) from 0-255 range.
        """
        r, g, b, a = self.item.color
        return r, g, b

    def set_color(self, r=0, g=0, b=0):
        """
        Sets the default port color in (red, green, blur, alpha) value.

        Args:
            r (int): red value 0-255 range.
            g (int): green value 0-255 range.
            b (int): blue value 0-255 range.
        """

        self.item.color = (r, g, b, 255)

    def connected_pipes(self):
        """
        Return all connected pipes.

        Returns:
            list[BlueprintNodeGraph.interfaces.Pipe]: list of pipe instances.
        """
        return [Pipe(p) for p in self.item.connected_pipes]

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[BlueprintNodeGraph.interfaces.Port]: list of connected ports.
        """
        self.node()
        return [Port(p.node, p) for p in self.item.connected_ports]

    def connect_to(self, port=None):
        """
        Creates a pipe and connects it to the port with a connection.

        Args:
            port (BlueprintNodeGraph.interfaces.Port): port object.
        """
        self.item.connect_to(port.item)


class Pipe(PipePlugin):

    @property
    def input(self):
        """
        return the connected input port.

        Returns:
            BlueprintNodeGraph.interfaces.Port: instance of the connected port.
        """
        port = self.item.input_port
        return Port(port.node, port)

    @property
    def output(self):
        """
        return the connect output port.

        Returns:
            BlueprintNodeGraph.interfaces.Port: instance of the connected port.
        """
        port = self.item.output_port
        return Port(port.node, port)

    def delete(self):
        """
        remove the connection pipe from the scene.
        """
        self.item.delete()
