from .node_base.subgraph_node import SubGraphNode, SubGraphInputNode, SubGraphOutputNode
import json
import os


class SubGraph(SubGraphNode):
    __identifier__ = 'Utility'

    # initial default node name.
    NODE_NAME = 'SubGraph'

    def __init__(self, defaultInputType=None, defaultOutputType=None, dynamic_port=True):
        super(SubGraph, self).__init__(defaultInputType, defaultOutputType, dynamic_port)
        self.create_property('create_from_select', True)

    def create_input_node(self, update=True):
        input_node = self.graph.create_node('Utility.SubGraphInput', pos=[-400, 200 * len(self.sub_graph_input_nodes)])
        input_node.set_property('input index', len(self.sub_graph_input_nodes))
        self.sub_graph_input_nodes.append(input_node)
        input_node.set_parent(self)
        if update:
            self.set_property('input count', self.get_property('input count') + 1)
            self.update_port()
        return input_node

    def create_output_node(self, update=True):
        output_node = self.graph.create_node('Utility.SubGraphOutput',
                                             pos=[400, 200 * len(self.sub_graph_output_nodes)])
        output_node.set_property('output index', len(self.sub_graph_output_nodes))
        self.sub_graph_output_nodes.append(output_node)
        output_node.set_parent(self)

        if update:
            self.set_property('output count', self.get_property('output count') + 1)
            self.update_port()
        return output_node

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

    def run(self):
        self.update_ports()
        super(SubGraph, self).run()

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
            
            self.graph.register_node(Publish.create_node_class(file_path))


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


def read_json(file_path):
    file_path = file_path.strip()
    if not os.path.isfile(file_path):
        raise IOError('node file {} does not exist.'.format(file_path))
    try:
        with open(file_path) as data_file:
            layout_data = json.load(data_file)
    except Exception as e:
        layout_data = None
        print('Cannot read data from file.\n{}'.format(e))
    return layout_data


class Publish(SubGraph):
    __identifier__ = '__None'
    NODE_NAME = '__None'
    NODE_FILE = None

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(Publish, self).__init__(defaultInputType, defaultOutputType, dynamic_port=False)
        self.set_property('color', (36, 97, 100, 255))
        self.create_property('published', True)
        self.created = False

    def set_graph(self, graph):
        super(Publish, self).set_graph(graph)
        if not self.created:
            self.create_from_file()
            self.created = True

    def create_from_file(self):
        if self.NODE_FILE is None:
            return
        data = read_json(self.NODE_FILE)
        if not data:
            return

        children_data = data.pop('sub_graph')
        n_data = data.pop('node')

        n_data.pop('name')
        # set properties.
        for prop in self.model.properties.keys():
            if prop in n_data.keys():
                self.model.set_property(prop, n_data[prop])
        # set custom properties.
        for prop, val in n_data.get('custom', {}).items():
            self.model.set_property(prop, val)

        if n_data.get('dynamic_port', None):
            self.set_ports({'input_ports': n_data['input_ports'], 'output_ports': n_data['output_ports']})

        children = self.graph._deserialize(children_data, set_parent=False)
        [node.set_parent(self) for node in children]

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        return

    @staticmethod
    def create_node_class(file_path):
        data = read_json(file_path)

        if not data:
            return None
        try:
            class_name =data['node']['class_name']
            new_node_class = type(class_name, (Publish,), {'NODE_FILE': file_path})
            new_node_class.__identifier__ = data['node']['__identifier__']
            new_node_class.NODE_NAME = data['node']['name']
            return new_node_class
        except:
            print('file {} is not a correct published node.'.format(file_path))
            return None