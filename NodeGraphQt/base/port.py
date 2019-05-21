#!/usr/bin/python
from NodeGraphQt.base.commands import (PortConnectedCmd,
                                       PortDisconnectedCmd,
                                       PortVisibleCmd)
from NodeGraphQt.base.model import PortModel


class Port(object):
    """
    base class for a node port.

    Args:
        node (NodeGraphQt.NodeObject): parent node.
        port (PortItem): graphic item used for drawing.
    """

    def __init__(self, node, port):
        self.__view = port
        self.__model = PortModel(node)

    def __repr__(self):
        port = str(self.__class__.__name__)
        return '<{}("{}") object at {}>'.format(port, self.name(), hex(id(self)))

    @property
    def view(self):
        """
        returns the :class:`QtWidgets.QGraphicsItem` used in the scene.

        Returns:
            NodeGraphQt.qgraphics.port.PortItem: port item.
        """
        return self.__view

    @property
    def model(self):
        """
        returns the port model.

        Returns:
            NodeGraphQt.base.model.PortModel: port model.
        """
        return self.__model

    def type_(self):
        """
        Returns the port type.

        Returns:
            str: 'in' for input port or 'out' for output port.
        """
        return self.model.type_

    def multi_connection(self):
        """
        Returns if the ports is a single connection or not.

        Returns:
            bool: false if port is a single connection port
        """
        return self.model.multi_connection

    def node(self):
        """
        Return the parent node.

        Returns:
            NodeGraphQt.NodeObject: parent node object.
        """
        return self.model.node

    def name(self):
        """
        Returns the port name.

        Returns:
            str: port name.
        """
        return self.model.name

    def visible(self):
        """
        Port visible in the node graph.

        Returns:
            bool: true if visible.
        """
        return self.model.visible

    def set_visible(self, visible=True):
        """
        Sets weather the port should be visible or not.

        Args:
            visible (bool): true if visible.
        """
        label = 'show' if visible else 'hide'
        undo_stack = self.node().graph.undo_stack()
        undo_stack.beginMacro('{} port {}'.format(label, self.name()))

        connected_ports = self.connected_ports()
        if connected_ports:
            for port in connected_ports:
                undo_stack.push(PortDisconnectedCmd(self, port))

        undo_stack.push(PortVisibleCmd(self))
        undo_stack.endMacro()

    def connected_ports(self):
        """
        Returns all connected ports.

        Returns:
            list[NodeGraphQt.Port]: list of connected ports.
        """
        ports = []
        graph = self.node().graph
        for node_id, port_names in self.model.connected_ports.items():
            for port_name in port_names:
                node = graph.get_node_by_id(node_id)
                if self.type_() == 'in':
                    ports.append(node.outputs()[port_name])
                elif self.type_() == 'out':
                    ports.append(node.inputs()[port_name])
        return ports

    def connect_to(self, port=None):
        """
        Create connection to the specified port.

        Args:
            port (NodeGraphQt.Port): port object.
        """
        if not port:
            return

        graph = self.node().graph
        viewer = graph.viewer()
        undo_stack = graph.undo_stack()

        undo_stack.beginMacro('connect port')

        pre_conn_port = None
        src_conn_ports = self.connected_ports()
        if not self.multi_connection() and src_conn_ports:
            pre_conn_port = src_conn_ports[0]

        if not port:
            if pre_conn_port:
                undo_stack.push(PortDisconnectedCmd(self, port))
            return

        if graph.acyclic() and viewer.acyclic_check(self.view, port.view):
            if pre_conn_port:
                undo_stack.push(PortDisconnectedCmd(self, pre_conn_port))
                return

        trg_conn_ports = port.connected_ports()
        if not port.multi_connection() and trg_conn_ports:
            dettached_port = trg_conn_ports[0]
            undo_stack.push(PortDisconnectedCmd(port, dettached_port))
        if pre_conn_port:
            undo_stack.push(PortDisconnectedCmd(self, pre_conn_port))

        undo_stack.push(PortConnectedCmd(self, port))
        undo_stack.endMacro()

        # emit "port_connected" signal from the parent graph.
        graph.port_connected.emit(self, port)

    def disconnect_from(self, port=None):
        """
        Disconnect from the specified port.

        Args:
            port (NodeGraphQt.Port): port object.
        """
        if not port:
            return
        graph = self.node().graph
        graph.undo_stack().push(PortDisconnectedCmd(self, port))
