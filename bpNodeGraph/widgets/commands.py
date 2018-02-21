#!/usr/bin/python
from PySide import QtGui


class NodesMoveCmd(QtGui.QUndoCommand):
    """
    Node position changed.
    """

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


class NodeConnectionCmd(QtGui.QUndoCommand):
    """
    Node connect/disconnect.
    """

    def __init__(self, from_port, to_port, mode=None):
        QtGui.QUndoCommand.__init__(self)
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


class NodeConnectionChangedCmd(QtGui.QUndoCommand):
    """
    Changing a existing pipe "targed port" to a non multi_connection "end port"
    with no existing connections.
    """

    def __init__(self, from_port, to_port, dettached_port):
        QtGui.QUndoCommand.__init__(self)
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


class NodeConnectionSwitchedCmd(QtGui.QUndoCommand):
    """
    Changing a existing pipe "targed port" to a non multi_connection "end port"
    that has a existing connection.
    """

    def __init__(self, from_port, to_port, dis_port, dettached_port=None):
        QtGui.QUndoCommand.__init__(self)
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
