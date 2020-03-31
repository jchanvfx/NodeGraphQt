from .node_base.subgraph_node import SubGraphNode, SubGraphInputNode, SubGraphOutputNode
from .node_base.auto_node import AutoNode


class SubGraph(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraph'

    def __init__(self):
        super(SubGraph, self).__init__()
        self.create_property('create_from_select', True)

    def create_input_node(self, update=True):
        input_node = self.graph.create_node('Utility.SubGraphInput', pos=[-400, 200 * len(self.sub_graph_input_nodes)])
        input_node.set_parent(self)
        input_node.set_property('input index', len(self.sub_graph_input_nodes))
        self.sub_graph_input_nodes.append(input_node)
        if update:
            self.set_property('input count', self.get_property('input count') + 1)
            self.update_port()
        return input_node

    def create_output_node(self, update=True):
        output_node = self.graph.create_node('Utility.SubGraphOutput',
                                             pos=[400, 200 * len(self.sub_graph_output_nodes)])
        output_node.set_parent(self)
        output_node.set_property('output index', len(self.sub_graph_output_nodes))
        self.sub_graph_output_nodes.append(output_node)
        if update:
            self.set_property('output count', self.get_property('output count') + 1)
            self.update_port()
        return output_node

    def create_from_nodes(self, nodes):
        if self in nodes:
            nodes.remove(self)
        [n.set_parent(self) for n in nodes]

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
                    in_map[ports[0]] = [[ports[1], len(self.sub_graph_input_nodes) - 1]]
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
                    out_map[ports[0]] = [[ports[1], len(self.sub_graph_output_nodes) - 1]]
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
                # if input_count > len(self.sub_graph_input_nodes):
                #     for i in range(input_count - len(self.sub_graph_input_nodes)):
                #         self.create_input_node(False)
            else:
                for i in range(current_input_count - input_count):
                    self.delete_input(current_input_count - i - 1)
            update = True

        if output_count != current_output_count:
            if output_count > current_output_count:
                for i in range(output_count - current_output_count):
                    self.add_output('output' + str(len(self.output_ports())))
                # if output_count > len(self.sub_graph_output_nodes):
                #     for i in range(output_count - len(self.sub_graph_output_nodes)):
                #         self.create_output_node(False)
            else:
                for i in range(current_output_count - output_count):
                    self.delete_output(current_output_count - i - 1)
            update = True

        if update:
            self.view.draw_node()

    def run(self):
        self.update_ports()
        super(SubGraph, self).run()


class RootGraph(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'RootGraph'

    def __init__(self):
        super(RootGraph, self).__init__()
        self.create_property('root', True)
        self.model.set_property('id', '0' * 13)

    def set_graph(self, graph):
        super(RootGraph, self).set_graph(graph)
        graph.set_node_space(self)


class SubGraphInput(SubGraphInputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphInput'

    def __init__(self):
        super(SubGraphInput, self).__init__()


class SubGraphOutput(SubGraphOutputNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraphOutput'

    def __init__(self):
        super(SubGraphOutput, self).__init__()
