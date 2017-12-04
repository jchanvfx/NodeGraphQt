import json
import os
from .node_utils import get_node


class SessionSerializer(object):

    def __init__(self, nodes, pipes):
        self.nodes = nodes
        self.pipes = pipes

    def serialize_node(self, node):
        """

        Args:
            node (NodeItem): node item.

        Returns:
            dict: serialized node.
        """
        node_serial = {
            'type': node.type,
            'icon': node.icon,
            'name': node.name,
            'color': node.color,
            'border': node.border_color,
            'selected': node.selected,
            'pos': (node.scenePos().x(), node.scenePos().y())
        }
        node_data = node.all_data(include_default=False)
        node_widgets = node.all_widgets()
        widgets = {k: wid.value for k, wid in node_widgets.items()}

        return {node.id: {
            'node': node_serial, 'widgets': widgets, 'data': node_data
        }}

    def serialize_pipe_connection(self, pipe):
        """

        Args:
            pipe (Pipe): pipe item.

        Returns:
            dict: serialized pipe.
        """
        return {
            'in': {pipe.input_port.node.id: pipe.input_port.name},
            'out': {pipe.output_port.node.id: pipe.output_port.name}
        }

    def serialize(self):
        node_serials = {}
        pipe_serials = []
        for node in self.nodes:
            serialized = self.serialize_node(node)
            node_serials.update(serialized)
        for pipe in self.pipes:
            serialized = self.serialize_pipe_connection(pipe)
            pipe_serials.append(serialized)
        serialized_data = {
            'nodes': node_serials,
            'connections': pipe_serials
        }
        return serialized_data

    def serialize_to_str(self):
        return json.dumps(self.serialize(), indent=2)

    def write(self, file_path):
        file_path = file_path.strip()
        with open(file_path, 'w') as file_out:
            json.dump(self.serialize(), file_out, indent=2)


class SessionLoader(object):

    def __init__(self, viewer):
        self.viewer = viewer
        self.data = None

    def parse_node(self, node_id, node_data):
        """
        Args:
            node_id (str): node id (uuid string)
            node_data (dict): node attrs

        Returns:
            tuple: NodeItem, xy pos
        """
        node_instance = get_node(node_data.get('type'))
        node = node_instance.item
        node.id = node_id
        node.name = node_data.get('name')
        node.icon = node_data.get('icon')
        node.color = node_data.get('color')
        node.border_color = node_data.get('border')
        node.selected = node_data.get('selected')
        node_widgets = node.item.widgets
        for name, value in node_data.get('widgets', {}).items():
            if node_widgets.get(name):
                node_widgets.get(name).value = value
        return node, node_data.get('pos', [0.0, 0.0])

    def parse_connection_ports(self, connections):
        """
        Args:
            connections (list[dict]):
                [{node.id: {'node': node_serial,'widgets': widgets}}]

        Returns:
            list[tuple]: <inport>, <outport>
        """
        nodes_dict = {n.id: n for n in self.viewer.all_nodes()}
        connection_ports = []
        for link in connections:
            if not (link.get('in') and link.get('out')):
                continue
            for nid, input_name in link['in'].items():
                node = nodes_dict.get(nid)
                in_port = None
                for port in node.inputs:
                    if port.name == input_name:
                        in_port = port
                        break
            for nid, output_name in link['out'].items():
                node = nodes_dict.get(nid)
                out_port = None
                for port in node.outputs:
                    if port.name == output_name:
                        out_port = port
                        break
            if in_port and out_port:
                connection_ports.append((in_port, out_port))
        return connection_ports

    def build_session(self, data):
        """
        Args:
            data (dict): {}

        Returns:

        """
        # node_data = [for nid, node in data.get('nodes')]
        connection_data = data.get('connections')

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

    def load_str(self, str_data):
        self.data = json.loads(str_data)
        return self.build_session()

    def load(self, file_path):
        if not os.path.isfile(file_path):
            return
        with open(file_path) as data_file:
            self.data = json.load(data_file)
        return self.build_session()
