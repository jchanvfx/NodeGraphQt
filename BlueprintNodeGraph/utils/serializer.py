import json
import os
from .node_utils import get_node

FILE_FORMAT = '.bpg'


class SessionSerializer(object):


    @classmethod
    def serialize_node(cls, node):
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
        widgets = {}
        node_data = node.all_data(include_default=False)
        for k, v in node_data.items():
            widgets[k] = v

        return {node.id: {'node': node_serial, 'widgets': widgets}}

    @classmethod
    def serialize_pipe_connection(cls, pipe):
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

    @classmethod
    def serialize_session(cls, nodes, pipes):
        """

        Args:
            nodes (list[NodeItem]):
            pipes (list[Pipe]):

        Returns:
            dict: {
                'nodes': {
                    }
                }
        """
        node_serials = {}
        pipe_serials = []
        for node in nodes:
            serialized = cls.serialize_node(node)
            node_serials.update(serialized)
        for pipe in pipes:
            serialized = cls.serialize_pipe_connection(pipe)
            pipe_serials.append(serialized)
        return {'nodes': node_serials, 'connections': pipe_serials}

    @classmethod
    def serial_to_str(cls, nodes, pipes, indent=2):
        """

        Args:
            nodes:
            pipes:
            indent:

        Returns:
            str:
        """
        session = cls.serialize_session(nodes, pipes)
        return json.dumps(session, indent=indent)


def write(session_serial, file_path):
    file_path = file_path.strip()
    if os.path.isfile(file_path):
        if not file_path.endswith(FILE_FORMAT):
            file_path = '{}{}'.format(file_path, FILE_FORMAT)
        with open(file_path, 'w') as file_out:
            json.dump(session_serial, file_out, indent=2)
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



    # TODO: wi[ section to work on here.

    def build_session(self):
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
