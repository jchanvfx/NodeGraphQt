from .auto_node import AutoNode
from NodeGraphQt.base.node import SubGraph


class SubGraphNode(AutoNode, SubGraph):
    """
    sub graph node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None, dynamic_port=True):
        super(SubGraphNode, self).__init__(defaultInputType, defaultOutputType)
        SubGraph.__init__(self)
        self.set_property('color', (127, 54, 93, 255))
        self.sub_graph_input_nodes = []
        self.sub_graph_output_nodes = []
        self.create_property('graph_rect', None)
        if dynamic_port:
            self.model.dynamic_port = True
            self.add_int_input('input count', 'input count', 0)
            self.add_int_input('output count', 'output count', 0)
        else:
            self.model.dynamic_port = False
            self.create_property('input count', 'input count', 0)
            self.create_property('output count', 'output count', 0)
        self._run_ports = []

    def add_run_ports(self, port):
        if port not in self._run_ports and port in self.input_ports():
            self._run_ports.append(port)

    def enter(self):
        self.hide()
        [n.show() for n in self.children()]
        rect = self.get_property('graph_rect')
        if rect:
            self.graph.set_graph_rect(rect)

    def exit(self):
        for n in self.children():
            n.hide()
            n.set_selected(False)
        self.set_property('graph_rect', self.graph.graph_rect())

    def show(self):
        super().show()
        self.update_port()

    def update_port(self):
        self.view.draw_node()

    def add_child(self, node):
        if node not in self._children:
            self._children.append(node)
            node._parent = self

        if self.has_property('root'):
            return

        if isinstance(node, SubGraphInputNode):
            if node not in self.sub_graph_input_nodes:
                self.sub_graph_input_nodes.append(node)

        if isinstance(node, SubGraphOutputNode):
            if node not in self.sub_graph_output_nodes:
                self.sub_graph_output_nodes.append(node)

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
        self.error('can\'t find matched index output node !!!')
        return self.defaultValue

    def run(self):
        for node in self.sub_graph_input_nodes:
            node._parent = self

        if self._run_ports:
            for port in self._run_ports:
                index = self.input_ports().index(port)
                for node in self.sub_graph_input_nodes:
                    if node.get_property('input index') == index:
                        node.cook()
            self._run_ports = []
        else:
            [node.cook() for node in self.sub_graph_input_nodes]

    def delete(self):
        self._view.delete()
        for child in self._children:
            child._parent = None

        if self._parent is not None:
            self._parent.remove_child(self)

    def children(self):
        return self._children


class SubGraphInputNode(AutoNode):
    """
    sub graph input node.
    """

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(SubGraphInputNode, self).__init__(defaultInputType, defaultOutputType)
        self.set_property('color', (40, 50, 66, 255))
        self.add_output('out')
        self.add_int_input('input index', 'input index', value=0)

    def getData(self, port):
        parent = self.parent()
        if parent is not None:
            from_port = self.get_parent_port(parent)
            if from_port:
                return from_port.node().getData(from_port)
            else:
                # can not find port
                return self.defaultValue
        else:
            # can not find parent
            return self.defaultValue

    def get_parent_port(self, parent=None):
        if parent is None:
            parent = self.parent()
        index = self.get_property('input index')
        if index < 0 or index >= len(parent.inputs()):
            self.error('input index out of range !!!')
            return None
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
        self.set_property('color', (40, 50, 66, 255))
        self.add_input('in')
        self.add_int_input('output index', 'output index', value=0)

    def getData(self, port=None):
        to_port = self.input(0)
        from_ports = to_port.connected_ports()
        if not from_ports:
            return self.defaultValue

        for from_port in from_ports:
            return from_port.node().getData(from_port)
