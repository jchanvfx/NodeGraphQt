import json
import os
from collections import defaultdict

from .constants import FILE_FORMAT
from .node import NodeItem


class NodeSerializer(object):

    def __init__(self, node):
        self._node = node
        self._data = defaultdict(lambda: None)

    @property
    def node(self):
        return self._node

    def _serialize_node(self):
        self._data[self.node.id] = {
            'pos': (self.node.scenePos().x(), self.node.scenePos().y()),
            'icon': self.node.icon,
            'name': self.node.name,
            'color': self.node.color,
            'border': self.node.border_color,
            'type': self.node.type
        }

    def _serialize_ports(self):
        self._data[self.node.id]['inputs'] = []
        self._data[self.node.id]['outputs'] = []
        for port in self._node.inputs:
            self._data[self.node.id]['inputs'].append(port.name)
        for port in self._node.outputs:
            self._data[self.node.id]['outputs'].append(port.name)

    def _serialize_data(self):
        node_data = self.node.all_data(False)
        for k, v in node_data.items():
            self._data[self.node.id]['data'][k] = v

    def serialize(self):
        self._serialize_node()
        self._serialize_ports()
        self._serialize_data()
        return self._data


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
        self._data['nodes'] = serialized_nodes
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

    def __init__(self, node_id, data):
        self._node = None
        self._position = None
        self._parse_data(node_id, data)

    def _parse_data(self, node_id, data):
        node = NodeItem(node_id)
        node.name = data.get('name', 'node')
        node.icon = data.get('icon')
        node.color = data.get('color')
        node.border_color = data.get('border')
        for port_name in data.get('inputs', []):
            node.add_input(port_name)
        for port_name in data.get('outputs', []):
            node.add_output(port_name)
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
        node_data = self.data.get('nodes')
        nodes = {}
        for node_id, node_data in node_data.items():
            node_builder = NodeItemBuilder(node_id, node_data)
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

    def load(self, file_path):
        if not os.path.isfile(file_path):
            return
        with open(file_path) as data_file:
            self.data = json.load(data_file)

        node_index = {}
        for node_id, node_pos in self.build_nodes().items():
            node, pos = node_pos
            self.viewer.add_node(node)
            node.setPos(pos[0], pos[1])
            node_index[node_id] = node
        connections = self.build_connections(node_index)
        for in_port, out_port in connections:
            self.viewer.connect_ports(in_port, out_port)
