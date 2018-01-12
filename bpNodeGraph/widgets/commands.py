#!/usr/bin/python
from PySide import QtGui


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


class NodeConnectedCmd(QtGui.QUndoCommand):

    def __init__(self, from_port, to_port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('connect node')
        self.from_port = from_port
        self.to_port = to_port

    def undo(self):
        self.from_port.disconnect_from(self.to_port)

    def redo(self):
        self.from_port.connect_to(self.to_port)


class NodeDisconnectedCmd(QtGui.QUndoCommand):

    def __init__(self, from_port, to_port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('disconnect node')
        self.from_port = from_port
        self.to_port = to_port

    def undo(self):
        self.from_port.connect_to(self.to_port)

    def redo(self):
        self.from_port.disconnect_from(self.to_port)


class NodeConnectionChangedCmd(QtGui.QUndoCommand):

    def __init__(self, from_port, to_port, prev_port):
        QtGui.QUndoCommand.__init__(self)
        self.setText('connection changed')
        self.from_port = from_port
        self.to_port = to_port
        self.prev_port = prev_port

    def undo(self):
        self.from_port.disconnect_from(self.to_port)
        self.from_port.connect_to(self.prev_port)

    def redo(self):
        self.from_port.disconnect_from(self.prev_port)
        self.from_port.connect_to(self.to_port)
