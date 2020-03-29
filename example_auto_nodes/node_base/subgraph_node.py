from .auto_node import AutoNode
from NodeGraphQt.base.node import SubGraph


class SubGraphNode(AutoNode, SubGraph):
    """
    sub graph node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphNode, self).__init__(defaultInputType, defaultOutputType)
        SubGraph.__init__(self)
        self.set_property('color', (200, 155, 70, 255))
        self.bind_input_nodes = []
        self.bind_output_nodes = []
        self.add_input('input0')
        self.add_output('output0')
        self.create_property('graph_rect', None)

    def set_graph(self, graph):
        super(SubGraphNode, self).set_graph(graph)
        self.create_from_nodes(graph.selected_nodes())

    def enter(self):
        self.hide()
        rect = self.get_property('graph_rect')
        if rect:
            self.graph.set_graph_rect(rect)

    def exit(self):
        self.set_property('graph_rect', self.graph.graph_rect())

    def show(self):
        super().show()
        self.view.draw_node()

    def add_child(self, node):
        if node not in self._children:
            self._children.append(node)

        if isinstance(node, BindInputNode):
            if node not in self.bind_input_nodes:
                node.set_property('input index', len(self.bind_input_nodes))
                self.bind_input_nodes.append(node)
                if len(self.inputs()) < len(self.bind_input_nodes):
                    self.add_input('input' + str(len(self.bind_input_nodes) - 1))

        if isinstance(node, BindOutputNode):
            if node not in self.bind_output_nodes:
                node.set_property('output index', len(self.bind_output_nodes))
                self.bind_output_nodes.append(node)
                if len(self.outputs()) < len(self.bind_output_nodes):
                    self.add_output('output' + str(len(self.bind_output_nodes) - 1))

    def remove_child(self, node):
        if node in self._children:
            self._children.remove(node)

        if isinstance(node, BindInputNode):
            if node in self.bind_input_nodes:
                self.bind_input_nodes.remove(node)
        if isinstance(node, BindOutputNode):
            if node in self.bind_output_nodes:
                self.bind_output_nodes.remove(node)

    def getData(self, port):
        index = int(port.name()[-1])
        for node in self.bind_output_nodes:
            if node.get_property('output index') == index:
                return node.getData(None)
        return self.defaultValue

    def run(self):
        for node in self.bind_input_nodes:
            node.cook()

    def delete(self):
        self._view.delete()
        for child in self._children:
            child.model.parent_id = None

        if self.parent_id is not None:
            self.parent().remove_child(self)

    def children(self):
        return self._children


class BindInputNode(AutoNode):
    """
    bind input node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(BindInputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (200, 155, 100, 255))
        self.add_output('out')
        self.add_int_input('input index', 'input index', value=0)

    def getData(self, port):
        parent = self.parent()
        if parent is not None:
            index = self.get_property('input index')
            index = min(max(0, index), len(parent.inputs()) - 1)
            to_port = parent.input(int(index))
            from_ports = to_port.connected_ports()
            if not from_ports:
                return self.defaultValue

            for from_port in from_ports:
                return from_port.node().getData(from_port)
        else:
            return self.defaultValue

    def set_parent(self, parent):
        super(BindInputNode, self).set_parent(parent)


class BindOutputNode(AutoNode):
    """
    bind output node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(BindOutputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (200, 155, 100, 255))
        self.add_input('in')
        self.add_int_input('output index', 'output index', value=0)

    def getData(self, port=None):
        to_port = self.input(0)
        from_ports = to_port.connected_ports()
        if not from_ports:
            return self.defaultValue

        for from_port in from_ports:
            return from_port.node().getData(from_port)
