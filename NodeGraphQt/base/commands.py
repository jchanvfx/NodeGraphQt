#!/usr/bin/python
from PySide2.QtWidgets import QUndoCommand


class PropertyChangedCmd(QUndoCommand):
    """
    Node property changed command.
    """

    def __init__(self, node, name, value):
        QUndoCommand.__init__(self)
        self.setText('set {} ({})'.format(name, node.name()))
        self.node = node
        self.name = name
        self.old_val = node.get_property(name)
        self.new_val = value

    def set_node_prop(self, name, value):
        # set model data.
        model = self.node.model
        if name in model.properties.keys():
            setattr(model, name, value)
        elif name in model.custom_properties.keys():
            model.custom_properties[name] = value
        else:
            raise KeyError('No property "{}"'.format(name))

        # set view data.
        view = self.node.view

        # view widgets.
        if hasattr(view, 'widgets') and name in view.widgets.keys():
            view.widgets[name].value = value

        # view properties.
        if name in view.properties.keys():
            setattr(view, name, value)

    def undo(self):
        if self.old_val != self.new_val:
            self.set_node_prop(self.name, self.old_val)

    def redo(self):
        if self.old_val != self.new_val:
            self.set_node_prop(self.name, self.new_val)


class NodeMovedCmd(QUndoCommand):
    """
    Node moved command.
    """

    def __init__(self, node, pos, prev_pos):
        QUndoCommand.__init__(self)
        self.node = node
        self.pos = pos
        self.prev_pos = prev_pos

    def undo(self):
        self.node.view.pos = self.prev_pos
        self.node.model.pos = self.prev_pos

    def redo(self):
        if self.pos == self.prev_pos:
            return
        self.node.view.pos = self.pos
        self.node.model.pos = self.pos


class NodeAddedCmd(QUndoCommand):
    """
    Node added command.
    """

    def __init__(self, graph, node, pos=None):
        QUndoCommand.__init__(self)
        self.setText('added node')
        self.graph = graph
        self.node = node
        self.pos = pos

    def undo(self):
        self.pos = self.pos or self.node.pos()
        self.graph.model.nodes.pop(self.node.id)
        self.node.view.delete()

    def redo(self):
        self.graph.model.nodes[self.node.id] = self.node
        self.graph.viewer().add_node(self.node.view, self.pos)


class NodeRemovedCmd(QUndoCommand):
    """
    Node deleted command.
    """

    def __init__(self, graph, node):
        QUndoCommand.__init__(self)
        self.setText('deleted node')
        self.graph = graph
        self.node = node
        self.inputs = []
        self.outputs = []
        if hasattr(self.node, 'inputs'):
            input_ports = self.node.inputs().values()
            self.inputs = [(p, p.connected_ports()) for p in input_ports]
        if hasattr(self.node, 'outputs'):
            output_ports = self.node.outputs().values()
            self.outputs = [(p, p.connected_ports()) for p in output_ports]

    def undo(self):
        self.graph.model.nodes[self.node.id] = self.node
        self.graph.scene().addItem(self.node.view)
        for port, connected_ports in self.inputs:
            [port.connect_to(p) for p in connected_ports]
        for port, connected_ports in self.outputs:
            [port.connect_to(p) for p in connected_ports]

    def redo(self):
        for port, connected_ports in self.inputs:
            [port.disconnect_from(p) for p in connected_ports]
        for port, connected_ports in self.outputs:
            [port.disconnect_from(p) for p in connected_ports]
        self.graph.model.nodes.pop(self.node.id)
        self.node.view.delete()


class PortConnectedCmd(QUndoCommand):
    """
    Port connected command.
    """

    def __init__(self, src_port, trg_port):
        QUndoCommand.__init__(self)
        self.source = src_port
        self.target = trg_port

    def undo(self):
        src_model = self.source.model
        trg_model = self.target.model
        src_id = self.source.node().id
        trg_id = self.target.node().id

        port_names = src_model.connected_ports.get(trg_id)
        if port_names is []:
            del src_model.connected_ports[trg_id]
        if port_names and self.target.name() in port_names:
            port_names.remove(self.target.name())

        port_names = trg_model.connected_ports.get(src_id)
        if port_names is []:
            del trg_model.connected_ports[src_id]
        if port_names and self.source.name() in port_names:
            port_names.remove(self.source.name())

        self.source.view.disconnect_from(self.target.view)

    def redo(self):
        src_model = self.source.model
        trg_model = self.target.model
        src_id = self.source.node().id
        trg_id = self.target.node().id

        src_model.connected_ports[trg_id].append(self.target.name())
        trg_model.connected_ports[src_id].append(self.source.name())

        self.source.view.connect_to(self.target.view)


class PortDisconnectedCmd(QUndoCommand):
    """
    Port disconnected command.
    """

    def __init__(self, src_port, trg_port):
        QUndoCommand.__init__(self)
        self.source = src_port
        self.target = trg_port

    def undo(self):
        src_model = self.source.model
        trg_model = self.target.model
        src_id = self.source.node().id
        trg_id = self.target.node().id

        src_model.connected_ports[trg_id].append(self.target.name())
        trg_model.connected_ports[src_id].append(self.source.name())

        self.source.view.connect_to(self.target.view)

    def redo(self):
        src_model = self.source.model
        trg_model = self.target.model
        src_id = self.source.node().id
        trg_id = self.target.node().id

        port_names = src_model.connected_ports.get(trg_id)
        if port_names is []:
            del src_model.connected_ports[trg_id]
        if port_names and self.target.name() in port_names:
            port_names.remove(self.target.name())

        port_names = trg_model.connected_ports.get(src_id)
        if port_names is []:
            del trg_model.connected_ports[src_id]
        if port_names and self.source.name() in port_names:
            port_names.remove(self.source.name())

        self.source.view.disconnect_from(self.target.view)
