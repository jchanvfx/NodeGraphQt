import json
import os


class NodeSerializer(object):

    def __init__(self, node):
        """
        Args:
            node (from BlueprintNodeGraph.widgets.node.NodeItem): node item
        """
        self.node = node
        self._data = {self._nid: {}}

    def serialize_node(self):
        node = {
            'type': self.node.type,
            'icon': self.node.icon,
            'name': self.node.name,
            'color': self.node.color,
            'border': self.node.border_color,
            'selected': self.node.selected,
            'pos': (self.node.scenePos().x(), self.node.scenePos().y())
        }
        return node

    def serialize_data(self):
        node_wids = {}
        node_data = self.node.all_data(include_default=False)
        for k, v in node_data.items():
            node_wids[k] = v
        return node_wids

    def serialize(self):
        node = {
            self._nid: {
                'node': self.serialize_node(), 'widget': self.serialize_data()
            }
        }
        return node


class PipeSerializer(object):

    def __init__(self, pipe):
        self._pipe = pipe


class SessionSerializer(object):

    def __init__(self):
        self._nodes = []
        self._pipes = []
        self._data = {}

    def set_nodes(self, nodes):
        self._nodes = nodes

    def set_pipes(self, pipes):
        self._pipes = pipes

    def serialize_nodes(self):
        serialized_nodes = {}
        for node in self._nodes:
            serializer = NodeSerializer(node)
            serialized_nodes.update(serializer.serialize())
        self._data['interfaces'] = serialized_nodes
        return serialized_nodes

    def serialize_pipes(self):
        serialized_pipes = []
        for pipe in self._pipes:
            connection = {
                'in': {pipe.input_port.node.id: pipe.input_port.name},
                'out': {pipe.output_port.node.id: pipe.output_port.name}
            }
            serialized_pipes.append(connection)
        self._data['links'] = serialized_pipes
        return serialized_pipes

    def serialize(self):
        self._data = {}
        self.serialize_nodes()
        self.serialize_pipes()
        return self._data

    def serialize_str(self, pretty=True):
        indent = 2 if pretty else None
        str_data = self.serialize()
        return json.dumps(str_data, indent=indent)

    def write(self, file_path):
        file_path = file_path.strip()
        if file_path:
            if not file_path.endswith(FILE_FORMAT):
                file_path = '{}{}'.format(file_path, FILE_FORMAT)
            session_data = self.serialize()
            with open(file_path, 'w') as file_out:
                json.dump(session_data, file_out, indent=4)
                return True
        return False


class NodeItemBuilder(object):

    def __init__(self, node_id, data, node_types):
        self._node = None
        self._position = None
        self._node_types = node_types
        self.parse_data(node_id, data)

    def node_object(self, node_type):
        return self._node_types[node_type]()

    def parse_data(self, node_id, data):
        node = self.node_object(data.get('type'))
        node.item.id = node_id
        node.item.name = data.get('name')
        node.item.icon = data.get('icon')
        node.item.color = data.get('color')
        node.item.border_color = data.get('border')
        node.item.selected = data.get('selected')
        node_widgets = node.item.widgets
        for name, value in data.get('knobs', {}).items():
            if node_widgets.get(name):
                node_widgets.get(name).value = value
        self._node = node
        self._position = data.get('pos', [0.0, 0.0])

    def node(self):
        return self._node

    def position(self):
        return self._position


class SessionLoader(object):

    def __init__(self, viewer):
        self.viewer = viewer
        self.data = None

    def build_nodes(self):
        node_types = registered_nodes()
        node_data = self.data.get('interfaces')
        nodes = {}
        for node_id, node_data in node_data.items():
            node_builder = NodeItemBuilder(node_id, node_data, node_types)
            node = node_builder.node()
            pos = node_builder.position()
            nodes[node_id] = (node, pos)
        return nodes

    def build_connections(self, node_ref):
        connection_ports = []
        for link in self.data.get('links'):
            if not (link.get('in') and link.get('out')):
                continue
            for nid, input_name in link['in'].items():
                node = node_ref.get(nid)
                in_port = None
                for port in node.inputs:
                    if port.name == input_name:
                        in_port = port
                        break
            for nid, output_name in link['out'].items():
                node = node_ref.get(nid)
                out_port = None
                for port in node.outputs:
                    if port.name == output_name:
                        out_port = port
                        break
            if in_port and out_port:
                connection_ports.append((in_port, out_port))
        return connection_ports

    def build(self):
        nodes = []
        node_index = {}
        for node_id, node_pos in self.build_nodes().items():
            node, pos = node_pos
            self.viewer.add_node(node.item)
            node.item.setPos(pos[0], pos[1])
            node_index[node_id] = node.item
            nodes.append(node.item)
        connections = self.build_connections(node_index)
        for in_port, out_port in connections:
            if in_port in out_port.connected_ports:
                continue
            if out_port in in_port.connected_ports:
                continue
            if in_port and out_port:
                self.viewer.connect_ports(in_port, out_port)

        for node in nodes:
            if node.selected:
                node._hightlight_pipes()
        return nodes

    def load_str(self, str_data):
        self.data = json.loads(str_data)
        return self.build()

    def load(self, file_path):
        if not os.path.isfile(file_path):
            return
        with open(file_path) as data_file:
            self.data = json.load(data_file)
        return self.build()
