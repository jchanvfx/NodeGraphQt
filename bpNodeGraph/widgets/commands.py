#!/usr/bin/python
from PySide import QtGui

from .constants import IN_PORT, OUT_PORT


class NodesMoveCmd(QtGui.QUndoCommand):

    def __init__(self, nodes):
        QtGui.QUndoCommand.__init__(self)
        self.setText('move node(s)')
        self.nodes = nodes
        self.from_pos = [n.prev_pos for n in self.nodes]
        self.to_pos = [n.pos for n in self.nodes]

    def undo(self):
        for idx, node in enumerate(self.nodes):
            node.pos = self.from_pos[idx]

    def redo(self):
        for idx, node in enumerate(self.nodes):
            node.pos = self.to_pos[idx]


class PortConnectedCmd(QtGui.QUndoCommand):

    def __init__(self, from_port, to_port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('connected node')
        self.from_port = from_port
        self.to_port = to_port

    def undo(self):
        port_types = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
        for pipe in self.from_port.connected_pipes:
            port = getattr(pipe, port_types[self.from_port.port_type])
            if port == self.to_port:
                pipe.delete()

    def redo(self):
        self.from_port.connect_to(self.to_port)


class PortDisconnectedCmd(QtGui.QUndoCommand):

    def __init__(self, from_port, to_port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('disconnected node')
        self.from_port = from_port
        self.to_port = to_port

    def undo(self):
        self.from_port.connect_to(self.to_port)

    def redo(self):
        port_types = {IN_PORT: 'output_port', OUT_PORT: 'input_port'}
        for pipe in self.from_port.connected_pipes:
            port = getattr(pipe, port_types[self.from_port.port_type])
            if port == self.to_port:
                pipe.delete()
