import json
import os

from .node import NodeItem
from .constants import FILE_FORMAT


class SessionSaver(object):
    """
    Session save to write node graph session (.ngraph) files.
    """

    def __init__(self, nodes, pipes):
        self.nodes = nodes
        self.pipes = pipes

    def _file_out(self, file_path, data):
        with open(file_path, 'w') as file_out:
            json.dump(data, file_out, indent=4)
            return True

    def _serialize_node(self, node):
        data = {
            # 'id': self.id,
            'pos': (node.scenePos().x(), node.scenePos().y()),
            'icon': node.icon,
            'name': node.name,
            'color': node.color,
            'border': node.border_color,
            'inputs': [],
            'outputs': []}
        for port in node.inputs:
            data['inputs'].append(port.name)
        for port in node.outputs:
            data['outputs'].append(port.name)
        return data

    def _serialize_connection(self, pipe):
        data = {
            'in': {pipe.input_port.node.id: pipe.input_port.name},
            'out': {pipe.output_port.node.id: pipe.output_port.name}
            }
        return data

    def save_session(self, file_path):
        if file_path and not file_path.endswith(FILE_FORMAT):
            file_path = '{}{}'.format(file_path.strip(), FILE_FORMAT)
        if not file_path:
            return
        data = {'nodes': {}, 'links': []}
        for node in self.nodes:
            data['nodes'][node.id] = self._serialize_node(node)
        for pipe in self.pipes:
            connection_data = self._serialize_connection(pipe)
            data['links'].append(connection_data)
        saved = self._file_out(file_path, data)
        return saved


class SessionLoader(object):
    """
    Session loader to parse node graph session (.ngraph) files.
    """

    def __init__(self, viewer):
        self.viewer = viewer
        self.file_path = None
        self.data = None

    def _file_in(self):
        if not os.path.isfile(self.file_path):
            return
        with open(self.file_path) as data_file:
            self.data = json.load(data_file)

    def _make_node_item(self, node_id, data):
        node = NodeItem(data.get('name'), node_id)
        node.icon = data.get('icon')
        node.color = data.get('color')
        node.border_color = data.get('border')
        for port_name in data.get('inputs', []):
            node.add_input(port_name)
        for port_name in data.get('outputs', []):
            node.add_output(port_name)
        position = data.get('pos', [0.0, 0.0])
        return node, position

    def _build_nodes(self):
        node_data = self.data.get('nodes')
        nodes = {}
        for nid, ndata in node_data.items():
            node_item, node_pos = self._make_node_item(nid, ndata)
            nodes[nid] = (node_item, node_pos)
        return nodes

    def _build_connections(self, node_ref):
        connection_ports = []
        connection_data = self.data.get('links')
        for link in connection_data:
            if not(link.get('in') and link.get('out')):
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

    def load_file(self, file_path):
        self.file_path = file_path
        self._file_in()
        nodes = self._build_nodes()
        node_ref = {}
        for nid, item_pos in nodes.items():
            node, pos = item_pos
            self.viewer.add_node(node)
            node.setPos(pos[0], pos[1])
            node_ref[nid] = node
        connections = self._build_connections(node_ref)
        for in_port, out_port in connections:
            self.viewer.connect_ports(in_port, out_port)
