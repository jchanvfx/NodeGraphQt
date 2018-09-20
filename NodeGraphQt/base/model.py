#!/usr/bin/python
import json
from collections import defaultdict


class PortModel(object):

    def __init__(self, node):
        self.node = node
        self.type = ''
        self.name = 'port'
        self.display_name = True
        self.multi_connection = False
        self.connected_ports = defaultdict(list)

    def __repr__(self):
        return '{}(\'{}\')'.format(self.__class__.__name__, self.name)

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node port dictionary eg.
                {
                    'type': 'in',
                    'name': 'port',
                    'display_name': True,
                    'multi_connection': False,
                    'connected_ports': {<node_id>: [<port_name>, <port_name>]}
                }
        """
        props = self.__dict__.copy()
        props.pop('node')
        props['connected_ports'] = dict(props.pop('connected_ports'))
        return props


class NodeModel(object):

    def __init__(self):
        self.type = None
        self.id = hex(id(self))
        self.icon = None
        self.name = 'node'
        self.color = (48, 58, 69, 255)
        self.border_color = (85, 100, 100, 255)
        self.text_color = (255, 255, 255, 180)
        self.disabled = False
        self.selected = False
        self.width = 100.0
        self.height = 80.0
        self.pos = (0.0, 0.0)
        self.inputs = {}
        self.outputs = {}
        self._properties = {}

    @property
    def properties(self):
        """
        return all default node properties.

        Returns:
            dict: default node properties.
        """
        props = self.__dict__.copy()
        props.pop('_properties')
        return props

    @property
    def custom_properties(self):
        """
        return all custom properties specified by the user.

        Returns:
            dict: user defined properties.
        """
        return self._properties

    @property
    def to_dict(self):
        """
        serialize model information to a dictionary.

        Returns:
            dict: node id as the key and properties as the values eg.
                {'0x106cf75a8': {
                    'name': 'foo node',
                    'color': (48, 58, 69, 255),
                    'border_color': (85, 100, 100, 255),
                    'text_color': (255, 255, 255, 180),
                    'type': 'com.chantasticvfx.FooNode',
                    'selected': False,
                    'disabled': False,
                    'inputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}},
                    'outputs': {
                        <port_name>: {<node_id>: [<port_name>, <port_name>]}},
                    'width': 0.0,
                    'height: 0.0,
                    'pos': (0.0, 0.0),
                    'custom': {},
                    }
                }
        """
        node_dict = self.__dict__.copy()
        node_id = node_dict.pop('id')

        inputs = {}
        outputs = {}
        for name, model in node_dict.pop('inputs').items():
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                inputs[name] = connected_ports
        for name, model in node_dict.pop('outputs').items():
            connected_ports = model.to_dict['connected_ports']
            if connected_ports:
                outputs[name] = connected_ports
        if inputs:
            node_dict['inputs'] = inputs
        if outputs:
            node_dict['outputs'] = outputs

        custom_props = node_dict.pop('_properties', {})
        if custom_props:
            node_dict['custom'] = custom_props

        return {node_id: node_dict}

    @property
    def serial(self):
        """
        Serialize model information to a string.

        Returns:
            str: serialized JSON string.
        """
        model_dict = self.to_dict
        return json.dumps(model_dict)


class NodeGraphModel(object):

    def __init__(self):
        self.nodes = {}
        self.session = ''
        self.acyclic = True


if __name__ == '__main__':
    p = PortModel(None)
    # print(p.to_dict)

    n = NodeModel()
    n.inputs[p.name] = p
    # print(n.properties)
    for k, v in n.to_dict[n.id].items():
        print(k, v)