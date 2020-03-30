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
        self.sub_graph_input_nodes = []
        self.sub_graph_output_nodes = []
        self.add_input('input0')
        self.add_output('output0')
        self.create_property('graph_rect', None)

    def enter(self):
        self.hide()
        [n.show() for n in self.children()]
        rect = self.get_property('graph_rect')
        if rect:
            self.graph.set_graph_rect(rect)

    def exit(self):
        [n.hide() for n in self.children()]
        self.set_property('graph_rect', self.graph.graph_rect())

    def show(self):
        super().show()
        self.view.draw_node()

    def add_child(self, node):
        if node not in self._children:
            self._children.append(node)

        if self.has_property('root'):
            return
        if isinstance(node, SubGraphInputNode):
            if node not in self.sub_graph_input_nodes:
                node.set_property('input index', len(self.sub_graph_input_nodes))
                self.sub_graph_input_nodes.append(node)
                if len(self.inputs()) < len(self.sub_graph_input_nodes):
                    self.add_input('input' + str(len(self.sub_graph_input_nodes) - 1))

        if isinstance(node, SubGraphOutputNode):
            if node not in self.sub_graph_output_nodes:
                node.set_property('output index', len(self.sub_graph_output_nodes))
                self.sub_graph_output_nodes.append(node)
                if len(self.outputs()) < len(self.sub_graph_output_nodes):
                    self.add_output('output' + str(len(self.sub_graph_output_nodes) - 1))

    def remove_child(self, node):
        if node in self._children:
            self._children.remove(node)

        if self.has_property('root'):
            return
        if isinstance(node, SubGraphInputNode):
            if node in self.sub_graph_input_nodes:
                self.sub_graph_input_nodes.remove(node)
        if isinstance(node, SubGraphOutputNode):
            if node in self.sub_graph_output_nodes:
                self.sub_graph_output_nodes.remove(node)

    def getData(self, port):
        index = int(port.name()[-1])
        for node in self.sub_graph_output_nodes:
            if node.get_property('output index') == index:
                return node.getData(None)
        return self.defaultValue

    def run(self):
        for node in self.sub_graph_input_nodes:
            node.cook()

    def delete(self):
        self._view.delete()
        for child in self._children:
            child.model.parent_id = None

        if self.parent_id is not None:
            self.parent().remove_child(self)

    def children(self):
        return self._children


class SubGraphInputNode(AutoNode):
    """
    sub graph input node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphInputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (200, 155, 100, 255))
        self.add_output('out')
        self.add_int_input('input index', 'input index', value=0)

    def getData(self, port):
        parent = self.parent()
        if parent is not None:
            from_port = self.get_map_port(parent)
            if from_port:
                return from_port.node().getData(from_port)
            else:
                return self.defaultValue
        else:
            return self.defaultValue

    def set_parent(self, parent):
        super(SubGraphInputNode, self).set_parent(parent)

    def get_map_port(self, parent=None):
        if parent is None:
            parent = self.parent()
        index = self.get_property('input index')
        index = min(max(0, index), len(parent.inputs()) - 1)
        to_port = parent.input(int(index))
        from_ports = to_port.connected_ports()
        if from_ports:
            return from_ports[0]
        else:
            return None


class SubGraphOutputNode(AutoNode):
    """
    sub graph output node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphOutputNode, self).__init__(defaultInputType, defaultOutputType)
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
