import json
import os

from ..base.node_vendor import NodeVendor


class SessionSerializer(object):

    def __init__(self, nodes=None, pipes=None):
        self.nodes = nodes or {}
        self.pipes = pipes or []

    def serialize_node(self, node):
        """
        Args:
            node (NodeItem): node item.

        Returns:
            dict: serialized node.
        """
        prop_defaults = {
            'icon': node.icon,
            'name': node.name,
            'color': node.color,
            'border_color': node.border_color,
            'selected': node.selected,
            'disabled': node.disabled,
            'pos': node.pos
        }
        ignore_prop = prop_defaults.keys() + ['id', 'type']
        node_data = {
            k: v for k, v in node.properties.items() if k not in ignore_prop}
        widgets = {k: wid.value for k, wid in node.widgets.items()}

        return {node.id: {
            'type': node.type,
            'node': prop_defaults,
            'widgets': widgets,
            'data': node_data
        }}

    def serialize_nodes(self, nodes):
        """
        Args:
            nodes (list[NodeItem]): list of nodes.

        Returns:
            dict: serialized nodes.
                {<node_id>: {
                    'type': node type,
                    'node': <attr_dict>,
                    'data': <data_dict>,
                    'widget': <widget_dict>}}
        """
        node_serials = {}
        for node in nodes:
            serialized = self.serialize_node(node)
            node_serials.update(serialized)
        return node_serials

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

    def serialize_layout(self, nodes=None, pipes=None):
        nodes = nodes or self.nodes
        pipes = pipes or self.pipes
        node_serials = {}
        pipe_serials = []
        for node in nodes:
            serialized = self.serialize_node(node)
            node_serials.update(serialized)
        for pipe in pipes:
            serialized = self.serialize_pipe_connection(pipe)
            pipe_serials.append(serialized)
        serialized_data = {
            'nodes': node_serials,
            'connections': pipe_serials
        }
        return serialized_data

    def serialize_to_str(self):
        return json.dumps(self.serialize_layout(), indent=2)

    def write(self, file_path):
        file_path = file_path.strip()
        with open(file_path, 'w') as file_out:
            json.dump(
                self.serialize_layout(),
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
            node_data (dict): node attributes.

        Returns:
            tuple: NodeItem, xy pos
        """
        node_instance = NodeVendor.create_node_instance(node_data.get('type'))
        node = node_instance.item
        node.id = node_id
        node.name = node_data.get('name')
        node.icon = node_data.get('icon')
        node.color = node_data.get('color')
        node.border_color = node_data.get('border')
        node.selected = node_data.get('selected', False)
        node.disabled = node_data.get('disabled', False)
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

    def load_data(self, data):
        """
        build the node layout from dict.

        {'nodes': {
            <node_id>: {
                'type': str,
                'node': <attr_dict>,
                'widget': <widget_dict>,
                'data': <data_dict>}},
        'connections': [{
            'in': [<node_id>, <port_name>],
            'out': [<node_id>, <port_name>]}]
        }

        Args:
            data (dict): node id and object {node_id: node_item}
        """
        nodes = {}
        for node_id, attrs in data.get('nodes', {}).items():
            NodeClass = NodeVendor.create_node_instance(attrs['type'])
            if not NodeClass:
                raise ImportError('"{}" node unavailable.'
                                  .format(attrs['type']))
            node = NodeClass().item
            # default settings.
            for k, v in attrs.get('node', {}).items():
                if hasattr(node, k):
                    setattr(node, k, v)
                # set node initial position.
                if k == 'pos':
                    node.prev_pos = v
            # set custom properties
            for k, v in attrs.get('data', {}).items():
                if node.has_property(k):
                    node.set_property(k, v)
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

        return nodes

    def load_str(self, str_data):
        """
        load nodes from string.

        Args:
            str_data (str): node data string.

        Returns:
            list[NodeItem]: list of node items.
        """
        data = {}
        try:
            data = json.loads(str_data)
        except Exception as e:
            print 'Cannot read data from clipboard.\n{}'.format(e)

        return [node for nid, node in self.load_data(data).items()]

    def load(self, file_path):
        """
        load nodes from file path.

        Args:
            file_path (str): path to the file.

        Returns:
            list[NodeItem]: list of node items.
        """
        data = {}
        if not os.path.isfile(file_path):
            return
        try:
            with open(file_path) as data_file:
                data = json.load(data_file)
        except Exception as e:
            print 'Cannot read data from clipboard.\n{}'.format(e)

        return [node for nid, node in self.load_data(data).items()]
