from .node_base import SubGraphNode, SubGraphInputNode, SubGraphOutputNode
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

    def publish(self, file_path, node_name, node_identifier, node_class_name):
        file_path = super(SubGraph, self).publish(file_path, node_name, node_identifier, node_class_name)
        if file_path:
            self.graph.register_node(Publish.create_node_class(file_path))


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
    """
    Read published sub graph file and create corresponding node class.
    """

    __identifier__ = '__None'
    NODE_NAME = '__None'
    NODE_FILE = None

    def __init__(self, defaultInputType=None, defaultOutputType=None):
        super(Publish, self).__init__(defaultInputType, defaultOutputType, dynamic_port=False)
        self.set_property('color', (36, 97, 100, 255))
        self.set_property('published', True)
        self.created = False
        self.create_by_deserialize = False

    def set_graph(self, graph):
        super(Publish, self).set_graph(graph)
        if not self.created:
            self.create_from_file()
            self.created = True

    def create_from_file(self):
        """
        Update node properties and create sub graph nodes by published node file.
        """

        if self.NODE_FILE is None or not self.get_property('published'):
            return
        data = read_json(self.NODE_FILE)
        if not data:
            return

        children_data = data.pop('sub_graph')

        if not self.create_by_deserialize:
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
        if self.get_property('published'):
            return
        super(Publish, self).publish(file_path, node_name, node_identifier, node_class_name)

    @staticmethod
    def create_node_class(file_path):
        """
        Create a new node class by published node file.

        Args:
            file_path(str): published node file path.
        """

        data = read_json(file_path)

        if not data:
            return None
        try:
            class_name = data['node']['class_name']
            new_node_class = type(class_name, (Publish,), {'NODE_FILE': file_path})
            new_node_class.__identifier__ = data['node']['__identifier__']
            new_node_class.NODE_NAME = data['node']['name']
            return new_node_class
        except:
            print('file {} is not a correct published node.'.format(file_path))
            return None
