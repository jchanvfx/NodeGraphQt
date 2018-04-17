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
        return node.to_dict()

    def serialize_nodes(self, nodes):
        """
        Args:
            nodes (list[NodeItem]): list of nodes.

        Returns:
            dict: serialized nodes {<node_id>: <node_dict>}
        """
        serials = {}
        for node in nodes:
            serials.update(node.to_dict())
        return serials

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
        """
        Args:
            nodes (list[NodeItem]): list of node items.
            pipes (list[Pipe]): list of pipe items.

        Returns:
            dict: serialized session layout.
                {
                    'nodes': {<node_id>: <node_dict>},
                        'connections': [{
                            'in': [<node_id>, <input_port.name>],
                            'out': [<node_id>, <output_port.name>]
                    }]
                }
        """
        nodes = nodes or self.nodes
        pipes = pipes or self.pipes
        node_serials = self.serialize_nodes(nodes)
        pipe_serials = [self.serialize_pipe_connection(p) for p in pipes]
        return {'nodes': node_serials, 'connections': pipe_serials}

    def serialize_to_str(self):
        """
        Returns:
            str: json string session layout.
        """
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
        node.from_dict(node_data)

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
            <node_id>: {<attr_dict>}
            },
        'connections': [{
            'in': [<node_id>, <port_name>],
            'out': [<node_id>, <port_name>]}
            ]
        }

        Args:
            data (dict): node id and object {node_id: node_item}
        """
        nodes = {}

        # parse the nodes.
        for node_id, attrs in data.get('nodes', {}).items():
            NodeClass = NodeVendor.create_node_instance(attrs['type'])
            if not NodeClass:
                ie = '"{}" node unavailable.'.format(attrs['type'])
                raise ImportError(ie)
            node = NodeClass().item

            # add the node
            self.viewer.add_node(node)

            # set the attributes.
            node.from_dict(attrs)
            nodes[node_id] = node

        # parse the connections.
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
            if node.selected and hasattr(node, 'hightlight_pipes'):
                node.hightlight_pipes()

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
