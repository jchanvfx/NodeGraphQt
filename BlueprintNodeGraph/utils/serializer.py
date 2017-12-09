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
            'icon': node.icon,
            'name': node.name,
            'color': node.color,
            'border_color': node.border_color,
            'selected': node.selected,
            'pos': node.pos
        }
        node_data = node.all_data(include_default=False)
        node_widgets = node.all_widgets()
        widgets = {k: wid.value for k, wid in node_widgets.items()}

        return {node.id: {
            'type': node.type,
            'node': node_serial,
            'widgets': widgets,
            'data': node_data
        }}

    def serialize_pipe_connection(self, pipe):
        """

        Args:
            pipe (Pipe): pipe item.

        Returns:
            dict: serialized pipe.
        """
        return {
            'in': [pipe.input_port.node.id, pipe.input_port.name],
            'out': [pipe.output_port.node.id, pipe.output_port.name]
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
            json.dump(self.serialize(),
                      file_out,
                      indent=2,
                      separators=(',', ':')
            )


class SessionLoader(object):

    def __init__(self, viewer):
        self.viewer = viewer

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

    def build_layout(self, data):
        """
        build the node layout.
        {
        'nodes': {
            <node_id>: {
                'node': <attr_dict>,
                'data': <data_dict>,
                'widget': <widget_dict>}},
        'connections': [{
            'in': [<node_id>, <port_name>],
            'out': [<node_id>, <port_name>]
            }]
        }

        Args:
            data (dict): layout data
        """
        nodes = {}
        for node_id, attrs in data.get('nodes', {}).items():
            NodeClass = get_node(attrs['type'])
            node = NodeClass().item
            # default settings.
            for k, v in attrs.get('node', {}).items():
                if hasattr(node, k):
                    setattr(node, k, v)
            # user settings data
            for k, v in attrs.get('data', {}).items():
                if node.has_data(k):
                    node.set_data(k, v)
            # widget settings.
            for k, v in attrs.get('widgets', {}).items():
                widget = node.get_widget(k)
                if widget:
                    widget.value = v
            self.viewer.add_node(node)

            nodes[node_id] = node

        for connection in data.get('connections', []):
            node_start = nodes.get(connection['in'][0])
            node_end = nodes.get(connection['out'][0])
            if not node_start and node_end:
                continue
            port_in = None
            if node_start.inputs:
                for p in node_start.inputs:
                    if p.name == connection['in'][1]:
                        port_in = p
                        break
            port_out = None
            if node_end.outputs:
                for p in node_end.outputs:
                    if p.name == connection['out'][1]:
                        port_out = p
                        break
            if port_in and port_out:
                self.viewer.connect_ports(port_in, port_out)

        for nid, node in nodes.items():
            if node.selected:
                node._hightlight_pipes()

    def load_str(self, str_data):
        data = json.loads(str_data)
        return self.build_layout(data)

    def load(self, file_path):
        if not os.path.isfile(file_path):
            return
        with open(file_path) as data_file:
            data = json.load(data_file)
        return self.build_layout(data)
