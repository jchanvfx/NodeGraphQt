#!/usr/bin/python
from PySide2 import QtWidgets


class NodeDisabledCmd(QtWidgets.QUndoCommand):
    """
    Node enabled/disabled.
    """

    def __init__(self, node):
        QtWidgets.QUndoCommand.__init__(self)
        self.node = node
        self.mode = node.disabled
        mode = 'enabled' if self.mode else 'disabled'
        self.setText('{} node'.format(mode))

    def undo(self):
        self.node.disabled = not self.mode

    def redo(self):
        self.node.disabled = self.mode


class NodeDeletedCmd(QtWidgets.QUndoCommand):
    """
    Node deleted command.
    """

    def __init__(self, node, scene):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('deleted node')
        self.scene = scene
        self.node = node
        self.inputs = {}
        self.outputs = {}

        if hasattr(self.node, 'inputs'):
            self.inputs = {p: p.connected_ports for p in self.node.inputs}
        if hasattr(self.node, 'outputs'):
            self.outputs = {p: p.connected_ports for p in self.node.outputs}

    def undo(self):
        self.scene.addItem(self.node)
        for p, ports in self.inputs.items():
            [p.connect_to(cp) for cp in ports]
        for p, ports in self.outputs.items():
            [p.connect_to(cp) for cp in ports]

    def redo(self):
        self.node.delete()


class NodePositionChangedCmd(QtWidgets.QUndoCommand):
    """
    Node position changed.
    """

    def __init__(self, node):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('node position changed')
        self.node = node
        self.pos = node.pos
        self.prev_pos = node.prev_pos

    def undo(self):
        self.node.pos = self.prev_pos

    def redo(self):
        self.node.pos = self.pos


class NodeConnectionCmd(QtWidgets.QUndoCommand):
    """
    Node connect/disconnect.
    """

    def __init__(self, from_port, to_port, mode=None):
        QtWidgets.QUndoCommand.__init__(self)
        self.mode = {'connect': 0, 'disconnect': 1}.get(mode)
        self.setText('{} node'.format(mode))
        self.from_port = from_port
        self.to_port = to_port

    def undo(self):
        if self.mode == 0:
            self.from_port.disconnect_from(self.to_port)
        else:
            self.from_port.connect_to(self.to_port)

    def redo(self):
        if self.mode == 0:
            self.to_port.connect_to(self.from_port)
        else:
            self.from_port.disconnect_from(self.to_port)


class NodeConnectionChangedCmd(QtWidgets.QUndoCommand):
    """
    Changing a existing pipe "targeted port" to a non
    multi_connection "end port" with no existing connections.
    """

    def __init__(self, from_port, to_port, dettached_port):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('connected changed')
        self.from_port = from_port
        self.to_port = to_port
        self.dettached_port = dettached_port

    def undo(self):
        self.from_port.disconnect_from(self.to_port)
        self.from_port.connect_to(self.dettached_port)

    def redo(self):
        self.from_port.disconnect_from(self.dettached_port)
        self.from_port.connect_to(self.to_port)


class NodeConnectionSwitchedCmd(QtWidgets.QUndoCommand):
    """
    Changing a existing pipe "targeted port" to a non
    multi_connection "end port" that has a existing connection.
    """

    def __init__(self, from_port, to_port, dis_port, dettached_port=None):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('connection switched')
        self.from_port = from_port
        self.to_port = to_port
        self.dis_port = dis_port
        self.dettached_port = dettached_port

    def undo(self):
        if self.dettached_port:
            self.from_port.connect_to(self.dettached_port)
        self.dis_port.connect_to(self.to_port)
        self.from_port.disconnect_from(self.to_port)

    def redo(self):
        if self.dettached_port:
            self.from_port.disconnect_from(self.dettached_port)
        self.dis_port.disconnect_from(self.to_port)
        self.from_port.connect_to(self.to_port)
