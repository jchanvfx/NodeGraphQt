#!/usr/bin/python
from PySide2 import QtWidgets

from .constants import IN_PORT, OUT_PORT
from .pipe import Pipe


class NodePropertyChangedCmd(QtWidgets.QUndoCommand):
    """
    Node property changed.
    """

    def __init__(self, node, name, value):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('modified node "{}"'.format(name))
        self.node = node
        self.name = name
        self.old_val = self.node.get_property(name)
        self.new_val = value

    def undo(self):
        self.node.set_property(self.name, self.old_val)

    def redo(self):
        self.node.set_property(self.name, self.new_val)


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


class NodeCreatedCommand(QtWidgets.QUndoCommand):
    """
    Node created command.
    """

    def __init__(self, node, scene):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('created node')
        self.scene = scene
        self.node = node

    def undo(self):
        self.node.delete()

    def redo(self):
        self.scene.addItem(self.node)


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


class NodeConnectedCmd(QtWidgets.QUndoCommand):
    """
    Port connected command.
    """

    def __init__(self, start_port, end_port):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('connected node')
        self.start_port = start_port
        self.end_port = end_port
        self.pipe = Pipe()

    def establish_connection(self, start_port, end_port, pipe):
        ports = {
            start_port.port_type: start_port,
            end_port.port_type: end_port
        }
        scene = start_port.scene()
        scene.addItem(pipe)
        pipe.set_connections(ports[IN_PORT], ports[OUT_PORT])
        pipe.draw_path(pipe.input_port, pipe.output_port)

    def undo(self):
        self.pipe.delete()

    def redo(self):
        if self.end_port in self.start_port.connected_ports:
            return
        self.establish_connection(self.start_port,
                                  self.end_port,
                                  self.pipe)


class NodeDisconnectedCmd(QtWidgets.QUndoCommand):
    """
    Node disconnected command.
    """

    def __init__(self, start_port, end_port):
        QtWidgets.QUndoCommand.__init__(self)
        self.setText('disconnected node')
        self.start_port = start_port
        self.end_port = end_port
        self.pipe = Pipe()

    def establish_connection(self, start_port, end_port, pipe):
        ports = {
            start_port.port_type: start_port,
            end_port.port_type: end_port
        }
        scene = start_port.scene()
        scene.addItem(pipe)
        pipe.set_connections(ports[IN_PORT], ports[OUT_PORT])
        pipe.draw_path(pipe.input_port, pipe.output_port)

    def undo(self):
        self.establish_connection(self.start_port,
                                  self.end_port,
                                  self.pipe)

    def redo(self):
        if self.end_port not in self.start_port.connected_ports:
            return
        for pipe in self.start_port.connected_pipes:
            if self.end_port in [pipe.input_port, pipe.output_port]:
                self.pipe = pipe
                self.pipe.delete()
                break


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
