from .auto_node import AutoNode
from NodeGraphQt import SubGraph
import json
from NodeGraphQt import topological_sort_by_down


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

    def add_run_port(self, port):
        """
        mark a port to be cooked.

        Args:
            port(Port)
        """

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
        self.model.set_property('graph_rect', self.graph.graph_rect())

    def show(self):
        super().show()
        self.update_port()

    def update_port(self):
        self.view.draw_node()

    def add_child(self, node):
        self._children.add(node)
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
        if self.disabled():
            return super(SubGraphNode, self).getData(port)

        index = int(port.name()[-1])
        for node in self.sub_graph_output_nodes:
            if node.get_property('output index') == index:
                return node.getData(None)
        self.error('can\'t find matched index output node !!!')
        return self.defaultValue

    def _show_error(self, message):
        if not self._error:
            self.defaultColor = self.get_property("color")

        self._error = True
        self.set_property('color', self.errorColor)
        self._update_tool_tip(message)

    def run(self):
        self.update_ports()

        for node in self.sub_graph_input_nodes:
            node._parent = self

        start_nodes = []
        if self._run_ports:
            for port in self._run_ports:
                index = self.input_ports().index(port)
                for node in self.sub_graph_input_nodes:
                    if node.get_property('input index') == index:
                        start_nodes.append(node)
            self._run_ports = []
        else:
            start_nodes = self.sub_graph_input_nodes

        nodes = topological_sort_by_down(start_nodes=start_nodes)

        for node in nodes:
            if node.disabled():
                node.when_disabled()
            else:
                node.cook()
            if node.error():
                break

    def delete(self):
        self._view.delete()
        for child in self._children:
            child._parent = None

        if self._parent is not None:
            self._parent.remove_child(self)

    def children(self):
        return list(self._children)

    def create_input_node(self, update=True):
        pass

    def create_output_node(self, update=True):
        pass

    def create_from_nodes(self, nodes):
        if self in nodes:
            nodes.remove(self)
        [n.set_parent(self) for n in nodes]

        self.set_property('input count', 0)
        self.set_property('output count', 0)

        in_connect = []
        out_connect = []
        connected = []

        for node in nodes:
            for port in node.input_ports():
                for pipe in port.view.connected_pipes:
                    if pipe.output_port.isVisible():
                        in_connect.append((pipe.output_port, pipe.input_port))
            for port in node.output_ports():
                for pipe in port.view.connected_pipes:
                    if pipe.input_port.isVisible():
                        out_connect.append((pipe.output_port, pipe.input_port))
        in_map = {}
        for idx, ports in enumerate(in_connect):
            if ports[0] in in_map.keys():
                in_map[ports[0]].append([ports[1], in_map[ports[0]][0][1]])
            else:
                self.create_input_node()
                if idx > 0:
                    in_map[ports[0]] = [[ports[1], len(self.input_ports()) - 1]]
                else:
                    in_map[ports[0]] = [[ports[1], 0]]

        for port0, data in in_map.items():
            for port_data in data:
                idx = port_data[1]
                connected.append((port0, self.input_ports()[idx].view))
                connected.append((self.sub_graph_input_nodes[idx].output_ports()[0].view, port_data[0]))

        out_map = {}
        for idx, ports in enumerate(out_connect):
            if ports[0] in out_map.keys():
                out_map[ports[0]].append([ports[1], out_map[ports[0]][0][1]])
            else:
                self.create_output_node()
                if idx > 0:
                    out_map[ports[0]] = [[ports[1], len(self.output_ports()) - 1]]
                else:
                    out_map[ports[0]] = [[ports[1], 0]]

        for port0, data in out_map.items():
            for port_data in data:
                idx = port_data[1]
                connected.append((port0, self.sub_graph_output_nodes[idx].input_ports()[0].view))
                connected.append((self.output_ports()[idx].view, port_data[0]))

        disconnected = in_connect + out_connect

        if disconnected or connected:
            self.graph._on_connection_changed(disconnected, connected)

        if len(self.input_ports()) == 0:
            self.create_input_node()
        if len(self.output_ports()) == 0:
            self.create_output_node()
        self.set_property('create_from_select', False)

    def update_ports(self):
        input_count = self.get_property('input count')
        output_count = self.get_property('output count')
        current_input_count = len(self.input_ports())
        current_output_count = len(self.output_ports())

        update = False
        if input_count != current_input_count:
            if input_count > current_input_count:
                for i in range(input_count - current_input_count):
                    self.add_input('input' + str(len(self.input_ports())))
            else:
                for i in range(current_input_count - input_count):
                    self.delete_input(current_input_count - i - 1)
            update = True

        if output_count != current_output_count:
            if output_count > current_output_count:
                for i in range(output_count - current_output_count):
                    self.add_output('output' + str(len(self.output_ports())))
            else:
                for i in range(current_output_count - output_count):
                    self.delete_output(current_output_count - i - 1)
            update = True

        if update:
            self.view.draw_node()

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        if file_path and node_name and node_identifier and node_class_name:
            serialized_data = self.graph._serialize([self])
            data = {'node': serialized_data['nodes'][self.id]}
            data['sub_graph'] = data['node'].pop('sub_graph')
            data['node']['__identifier__'] = node_identifier
            data['node']['name'] = node_name
            data['node']['class_name'] = node_class_name.replace(" ", "_")
            data['node'].pop('type_')
            file_path = file_path.strip()
            with open(file_path, 'w') as file_out:
                json.dump(data, file_out, indent=2, separators=(',', ':'))
            return file_path
        return None


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


class RootNode(SubGraphNode):
    __identifier__ = '__None'

    # initial default node name.
    NODE_NAME = 'root'

    def __init__(self):
        super(RootNode, self).__init__()
        self.create_property('root', True)
        self.model.set_property('id', '0' * 13)

    def set_graph(self, graph):
        super(RootNode, self).set_graph(graph)
        graph.set_node_space(self)

    def cook(self):
        pass

    def run(self):
        pass

    def error(self, message=None):
        if message is None:
            return False
        self._error = False